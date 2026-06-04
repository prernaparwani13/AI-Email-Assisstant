# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

class UserResponse(UserBase):
    id: int
    google_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class EmailMessage(BaseModel):
    id: str
    thread_id: Optional[str] = None
    subject: Optional[str] = "No Subject"
    sender: Optional[str] = None
    sender_name: Optional[str] = None
    recipient: Optional[str] = None
    snippet: Optional[str] = None
    body: Optional[str] = None
    date: Optional[str] = None
    is_read: bool = False
    labels: Optional[List[str]] = []
    ai_category: Optional[str] = None
    ai_summary: Optional[str] = None

class EmailListResponse(BaseModel):
    emails: List[EmailMessage]
    next_page_token: Optional[str] = None
    total: int

class AIReplyRequest(BaseModel):
    email_body: str
    email_subject: Optional[str] = ""
    tone: Optional[str] = "professional"
    additional_context: Optional[str] = ""

class AISummarizeRequest(BaseModel):
    email_body: str
    email_subject: Optional[str] = ""

class AIGrammarRequest(BaseModel):
    text: str

class AIClassifyRequest(BaseModel):
    email_subject: Optional[str] = ""
    email_body: str
    sender: Optional[str] = ""

class AIResponse(BaseModel):
    result: str
    tokens_used: Optional[int] = None

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 20
