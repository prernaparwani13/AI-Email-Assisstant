# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmailCache(Base):
    __tablename__ = "email_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    gmail_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=True)
    subject = Column(Text, nullable=True)
    sender = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    labels = Column(Text, nullable=True)
    ai_category = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
