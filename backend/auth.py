import os
import jwt
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from fastapi import HTTPException, Depends, status
# pyrefly: ignore [missing-import]
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2.credentials import Credentials
# pyrefly: ignore [missing-import]
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from database import get_db
from models import User
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Dynamic env helpers — read on every call so no restart needed after .env edits
# ---------------------------------------------------------------------------

def _get(key: str, default: str = "") -> str:
    load_dotenv(override=True)
    return os.getenv(key, default)

def get_google_client_id() -> str:
    return _get("GOOGLE_CLIENT_ID")

def get_google_client_secret() -> str:
    return _get("GOOGLE_CLIENT_SECRET")

def get_google_redirect_uri() -> str:
    return _get("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

def get_jwt_secret_key() -> str:
    return _get("JWT_SECRET_KEY", "fallback_secret_key")

def get_jwt_algorithm() -> str:
    return _get("JWT_ALGORITHM", "HS256")

def get_jwt_expire_minutes() -> int:
    return int(_get("JWT_EXPIRE_MINUTES", "60"))

# ---------------------------------------------------------------------------
# OAuth scopes & security
# ---------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

security = HTTPBearer()

# ---------------------------------------------------------------------------
# Google OAuth helpers
# ---------------------------------------------------------------------------

def get_google_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": get_google_client_id(),
            "client_secret": get_google_client_secret(),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_google_redirect_uri()],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=get_google_redirect_uri(),
    )


def get_authorization_url():
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        # "select_account" forces Google to show the account picker every time,
        # so users can log in with any Gmail account, not just the last-used one.
        # "consent" ensures refresh_token is always returned.
        prompt="select_account consent",
    )
    return auth_url, state


def exchange_code_for_tokens(code: str):
    flow = get_google_flow()
    flow.fetch_token(code=code)
    return flow.credentials


def get_user_info(credentials: Credentials):
    service = build("oauth2", "v2", credentials=credentials)
    return service.userinfo().get().execute()


def get_google_credentials(user: User) -> Credentials:
    creds = Credentials(
        token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=get_google_client_id(),
        client_secret=get_google_client_secret(),
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # TODO: persist refreshed token back to DB if needed
    return creds

# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_jwt_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=get_jwt_expire_minutes())
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, get_jwt_secret_key(), algorithm=get_jwt_algorithm())


def verify_jwt_token(token: str) -> dict:
    # Dev-mode bypass
    if token == "mock_jwt_token_for_dev":
        return {"sub": "999999", "email": "developer@example.com", "name": "Developer Account"}
    try:
        return jwt.decode(token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ---------------------------------------------------------------------------
# FastAPI dependency: current authenticated user
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = verify_jwt_token(token)
    sub_val = payload.get("sub")

    # Dev-mode mock user
    if sub_val == "999999":
        user = db.query(User).filter(User.google_id == "mock_dev_user_123").first()
        if not user:
            user = User(
                google_id="mock_dev_user_123",
                email="developer@example.com",
                name="Developer Account",
                picture="https://www.gravatar.com/avatar/?d=mp",
                access_token="mock_access_token",
                refresh_token="mock_refresh_token",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    user_id = int(sub_val)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def upsert_user(
    db: Session,
    google_id: str,
    email: str,
    name: str,
    picture: str,
    access_token: str,
    refresh_token: str,
    token_expiry=None,
) -> User:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        user.access_token = access_token
        if refresh_token:
            user.refresh_token = refresh_token
        user.token_expiry = token_expiry
        user.name = name
        user.picture = picture
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user
