import os
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException, Query, status
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import RedirectResponse, JSONResponse
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from database import engine, get_db, Base
import models
from auth import (
    get_authorization_url, exchange_code_for_tokens, get_user_info,
    create_jwt_token, get_current_user, upsert_user,
)
from gmail import (
    fetch_emails, fetch_email_by_id, search_emails,
    send_email, mark_as_read, trash_email,
)
from ai import (
    generate_email_reply, summarize_email,
    correct_grammar, classify_email, compose_email_ai,
)
from schemas import (
    TokenResponse, UserResponse, EmailListResponse, EmailMessage,
    AIReplyRequest, AISummarizeRequest, AIGrammarRequest, AIClassifyRequest,
    AIResponse, SendEmailRequest,
)

load_dotenv(override=True)


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Email Assistant API",
    description="Full-stack AI Email Assistant powered by Gmail API and Google Gemini",
    version="1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Email Assistant API"}

# ─── Auth ─────────────────────────────────────────────────────────────────────

PLACEHOLDER_CLIENT_ID = "mock_client_id.apps.googleusercontent.com"
PLACEHOLDER_CLIENT_SECRET = "mock_client_secret"

@app.get("/auth/login")
def google_login():
    """Redirect user to Google OAuth consent screen.
    Falls back to dev-mock ONLY when credentials are absent or still using placeholder values.
    """
    load_dotenv(override=True)
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    is_placeholder = (
        not client_id
        or not client_secret
        or client_id == PLACEHOLDER_CLIENT_ID
        or client_secret == PLACEHOLDER_CLIENT_SECRET
    )

    if is_placeholder:
        # Dev-mode: no real credentials configured → bypass OAuth
        return {"auth_url": f"{FRONTEND_URL}/auth/callback?token=mock_jwt_token_for_dev"}

    try:
        auth_url, _ = get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"[auth/login] OAuth URL error: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth configuration error: {str(e)}")


@app.get("/auth/callback")
def google_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """Handle Google OAuth callback, exchange code for tokens."""
    try:
        credentials = exchange_code_for_tokens(code)
        user_info = get_user_info(credentials)
        
        user = upsert_user(
            db=db,
            google_id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture", ""),
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry,
        )
        
        jwt_token = create_jwt_token(user.id, user.email)
        
        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ─── Emails ───────────────────────────────────────────────────────────────────

@app.get("/emails", response_model=EmailListResponse)
def get_inbox(
    max_results: int = Query(default=30, ge=1, le=100),
    page_token: str = Query(default=None),
    label: str = Query(default="INBOX"),
    current_user: models.User = Depends(get_current_user),
):
    """Fetch emails from Gmail for the given label (INBOX, SENT, STARRED, TRASH…)."""
    try:
        result = fetch_emails(
            current_user,
            max_results=max_results,
            page_token=page_token,
            label_ids=[label],
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@app.get("/emails/{email_id}", response_model=EmailMessage)
def get_email(
    email_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Fetch a single email by ID."""
    try:
        email = fetch_email_by_id(current_user, email_id)
        # Auto mark as read
        try:
            mark_as_read(current_user, email_id)
        except:
            pass
        return email
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email: {str(e)}")

@app.post("/emails/{email_id}/read")
def mark_email_read(
    email_id: str,
    current_user: models.User = Depends(get_current_user),
):
    try:
        mark_as_read(current_user, email_id)
        return {"status": "success", "message": "Email marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/emails/{email_id}")
def delete_email(
    email_id: str,
    current_user: models.User = Depends(get_current_user),
):
    try:
        trash_email(current_user, email_id)
        return {"status": "success", "message": "Email moved to trash"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/search/query")
def search_emails_endpoint(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(default=20, ge=1, le=100),
    current_user: models.User = Depends(get_current_user),
):
    """Search Gmail emails."""
    try:
        result = search_emails(current_user, query=q, max_results=max_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/emails/send")
def send_email_endpoint(
    request: SendEmailRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Send an email via Gmail API."""
    try:
        result = send_email(
            user=current_user,
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc,
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# ─── AI Features ──────────────────────────────────────────────────────────────

@app.post("/ai/reply", response_model=AIResponse)
def ai_generate_reply(
    request: AIReplyRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Generate an AI email reply using Gemini."""
    try:
        reply = generate_email_reply(
            email_body=request.email_body,
            email_subject=request.email_subject,
            tone=request.tone,
            additional_context=request.additional_context,
        )
        return AIResponse(result=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI reply failed: {str(e)}")

@app.post("/ai/summarize", response_model=AIResponse)
def ai_summarize(
    request: AISummarizeRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Summarize an email using Gemini."""
    try:
        summary = summarize_email(request.email_body, request.email_subject)
        return AIResponse(result=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI summarize failed: {str(e)}")

@app.post("/ai/grammar", response_model=AIResponse)
def ai_grammar_correct(
    request: AIGrammarRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Correct grammar using Gemini."""
    try:
        corrected = correct_grammar(request.text)
        return AIResponse(result=corrected)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grammar correction failed: {str(e)}")

@app.post("/ai/classify", response_model=AIResponse)
def ai_classify(
    request: AIClassifyRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Classify an email using Gemini."""
    try:
        category = classify_email(
            email_subject=request.email_subject,
            email_body=request.email_body,
            sender=request.sender,
        )
        return AIResponse(result=category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/ai/compose", response_model=AIResponse)
def ai_compose(
    prompt: str = Query(...),
    tone: str = Query(default="professional"),
    current_user: models.User = Depends(get_current_user),
):
    """AI-compose a new email from a prompt."""
    from datetime import date
    try:
        today = date.today().strftime("%d/%m/%Y")
        composed = compose_email_ai(
            prompt_text=prompt,
            tone=tone,
            user_name=current_user.name or "",
            today_date=today,
        )
        return AIResponse(result=composed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compose failed: {str(e)}")

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
