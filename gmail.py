import os
import base64
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from auth import get_google_credentials
from models import User
from schemas import EmailMessage

MOCK_EMAILS = [
    {
        "id": "mock_1",
        "thread_id": "thread_1",
        "subject": "Urgent: Project Deadline Alignment",
        "sender": "sarah.manager@company.com",
        "sender_name": "Sarah Connor",
        "recipient": "developer@example.com",
        "snippet": "Hi Team, we need to finalize the API schema for the AI Email Assistant by end of day today.",
        "body": "Hi Team,\n\nWe need to finalize the API schema for the AI Email Assistant by the end of day today to stay on track for the release next week. Please review the updated schemas.py file and provide your feedback as soon as possible.\n\nThanks,\nSarah Connor\nEngineering Manager",
        "date": "Thu, 28 May 2026 10:15:00 +0000",
        "is_read": False,
        "labels": ["INBOX", "UNREAD"],
        "ai_category": "Work"
    },
    {
        "id": "mock_2",
        "thread_id": "thread_2",
        "subject": "Hey! Coffee this Friday?",
        "sender": "alex.friend@gmail.com",
        "sender_name": "Alex Mercer",
        "recipient": "developer@example.com",
        "snippet": "Long time no see. Let's catch up over coffee this Friday at 4 PM near your office.",
        "body": "Hey mate,\n\nLong time no see! I will be in your area this Friday afternoon. Let's catch up over coffee around 4 PM near your office if you are free. Let me know if that works!\n\nBest,\nAlex",
        "date": "Thu, 28 May 2026 09:30:00 +0000",
        "is_read": True,
        "labels": ["INBOX", "STARRED"],
        "ai_category": "Personal"
    },
    {
        "id": "mock_3",
        "thread_id": "thread_3",
        "subject": "Monthly Statement - April 2026",
        "sender": "alerts@chasebank.com",
        "sender_name": "Chase Bank Alerts",
        "recipient": "developer@example.com",
        "snippet": "Your monthly credit card statement for April 2026 is now available online.",
        "body": "Dear Customer,\n\nYour monthly credit card statement for the billing period ending April 30, 2026 is now available online. Please log in to your account to view your statement and make a payment.\n\nMinimum payment due: $35.00\nPayment due date: June 5, 2026\n\nThank you for choosing Chase.",
        "date": "Wed, 27 May 2026 14:22:00 +0000",
        "is_read": True,
        "labels": ["INBOX"],
        "ai_category": "Finance"
    },
    {
        "id": "mock_4",
        "thread_id": "thread_4",
        "subject": "🚀 AI Weekly: The Rise of Agentic AI workflows",
        "sender": "newsletter@aiweekly.co",
        "sender_name": "AI Weekly",
        "recipient": "developer@example.com",
        "snippet": "This week we dive deep into agentic workflows, multi-agent frameworks, and local LLMs.",
        "body": "Welcome to AI Weekly!\n\nThis week, we are looking at the massive shift from conversational chat interfaces to autonomous agentic workflows. Leading labs are moving toward systems that can plan, execute terminal commands, and browse the web autonomously to solve engineering tasks.\n\nHere are the top 3 open-source frameworks you should check out today...\n\nUntil next week,\nThe AI Weekly Team",
        "date": "Tue, 26 May 2026 08:00:00 +0000",
        "is_read": False,
        "labels": ["INBOX", "UNREAD"],
        "ai_category": "Newsletter"
    },
    {
        "id": "mock_5",
        "thread_id": "thread_5",
        "subject": "Special Offer: 50% off all courses this weekend",
        "sender": "marketing@udemy-edu.com",
        "sender_name": "Udemy Special Offers",
        "recipient": "developer@example.com",
        "snippet": "Expand your skillset with 50% discount on Web Development, Python, and Machine Learning.",
        "body": "Hi Learner,\n\nFor the next 48 hours only, get 50% off on all our top-rated courses. Whether you want to master Python, learn React, or start with Generative AI, we have you covered.\n\nClick the link below to apply the discount code automatically: WEEKEND50\n\nHappy learning!",
        "date": "Mon, 25 May 2026 17:45:00 +0000",
        "is_read": True,
        "labels": ["INBOX"],
        "ai_category": "Promotions"
    },
    {
        "id": "mock_sent_1",
        "thread_id": "thread_sent_1",
        "subject": "Re: Project Deadline Alignment",
        "sender": "developer@example.com",
        "sender_name": "Developer Account",
        "recipient": "sarah.manager@company.com",
        "snippet": "Hi Sarah, I've checked the schemas.py file. Everything looks good to me.",
        "body": "Hi Sarah,\n\nI've checked the schemas.py file and everything looks good to me. I have verified that all requirements are covered.\n\nBest,\nDeveloper",
        "date": "Thu, 28 May 2026 11:30:00 +0000",
        "is_read": True,
        "labels": ["SENT"],
        "ai_category": "Work"
    },
    {
        "id": "mock_trash_1",
        "thread_id": "thread_trash_1",
        "subject": "Old Newsletter - January Digest",
        "sender": "digest@techdigest.io",
        "sender_name": "Tech Digest",
        "recipient": "developer@example.com",
        "snippet": "Your January tech digest is here. Check out the top stories of the month.",
        "body": "Hi Developer,\n\nHere is your January Tech Digest. This month's top stories cover AI breakthroughs, new developer tools, and open-source projects worth following.\n\nStay curious,\nThe Tech Digest Team",
        "date": "Fri, 10 Jan 2026 09:00:00 +0000",
        "is_read": True,
        "labels": ["TRASH"],
        "ai_category": "Newsletter"
    }
]

def get_gmail_service(user: User):
    creds = get_google_credentials(user)
    service = build("gmail", "v1", credentials=creds)
    return service

def parse_email_headers(headers: List[Dict]) -> Dict[str, str]:
    result = {}
    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")
        if name in ["subject", "from", "to", "date", "cc", "bcc", "message-id"]:
            result[name] = value
    return result

def decode_email_body(payload: Dict) -> str:
    body = ""
    if "body" in payload and payload["body"].get("data"):
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    elif "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
                    break
            elif mime_type == "text/html" and not body:
                data = part.get("body", {}).get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
            elif mime_type.startswith("multipart/"):
                sub_body = decode_email_body(part)
                if sub_body:
                    body = sub_body
    return body

def parse_sender(from_header: str):
    """Extract name and email from From header."""
    if "<" in from_header:
        parts = from_header.split("<")
        name = parts[0].strip().strip('"')
        email_addr = parts[1].rstrip(">").strip()
        return name, email_addr
    return from_header, from_header

def fetch_emails(user: User, max_results: int = 30, page_token: Optional[str] = None,
                 label_ids: Optional[List[str]] = None) -> Dict:
    if user.google_id == "mock_dev_user_123":
        target_label = label_ids[0] if label_ids else "INBOX"
        filtered = [
            EmailMessage(**msg) for msg in MOCK_EMAILS
            if target_label in msg["labels"]
        ]
        return {
            "emails": filtered,
            "next_page_token": None,
            "total": len(filtered)
        }

    service = get_gmail_service(user)
    params = {
        "userId": "me",
        "maxResults": max_results,
    }
    if page_token:
        params["pageToken"] = page_token
    if label_ids:
        params["labelIds"] = label_ids
    else:
        params["labelIds"] = ["INBOX"]
    
    result = service.users().messages().list(**params).execute()
    messages = result.get("messages", [])
    next_page_token = result.get("nextPageToken")
    
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        email_obj = parse_message(msg_data)
        emails.append(email_obj)
    
    return {
        "emails": emails,
        "next_page_token": next_page_token,
        "total": len(emails),
    }

def fetch_email_by_id(user: User, email_id: str) -> EmailMessage:
    if user.google_id == "mock_dev_user_123":
        for msg in MOCK_EMAILS:
            if msg["id"] == email_id:
                return EmailMessage(**msg)
        return EmailMessage(
            id=email_id,
            subject="Mock Subject",
            sender="mock@example.com",
            body="Mock body",
            labels=["INBOX"]
        )

    service = get_gmail_service(user)
    msg_data = service.users().messages().get(
        userId="me", id=email_id, format="full"
    ).execute()
    return parse_message(msg_data)

def parse_message(msg_data: Dict) -> EmailMessage:
    headers = parse_email_headers(msg_data.get("payload", {}).get("headers", []))
    body = decode_email_body(msg_data.get("payload", {}))
    labels = msg_data.get("labelIds", [])
    
    sender_raw = headers.get("from", "")
    sender_name, sender_email = parse_sender(sender_raw)
    
    return EmailMessage(
        id=msg_data["id"],
        thread_id=msg_data.get("threadId"),
        subject=headers.get("subject", "No Subject"),
        sender=sender_email,
        sender_name=sender_name,
        recipient=headers.get("to", ""),
        snippet=msg_data.get("snippet", ""),
        body=body,
        date=headers.get("date", ""),
        is_read="UNREAD" not in labels,
        labels=labels,
    )

def search_emails(user: User, query: str, max_results: int = 20) -> Dict:
    if user.google_id == "mock_dev_user_123":
        q = query.lower()
        filtered = [
            EmailMessage(**msg) for msg in MOCK_EMAILS
            if q in msg["subject"].lower() or q in msg["body"].lower() or q in msg["sender"].lower()
        ]
        return {"emails": filtered, "total": len(filtered)}

    service = get_gmail_service(user)
    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    
    messages = result.get("messages", [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        emails.append(parse_message(msg_data))
    
    return {"emails": emails, "total": len(emails)}

def send_email(user: User, to: str, subject: str, body: str,
               cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict:
    if user.google_id == "mock_dev_user_123":
        new_sent_email = {
            "id": f"mock_sent_{len(MOCK_EMAILS) + 1}",
            "thread_id": "thread_sent_new",
            "subject": subject,
            "sender": "developer@example.com",
            "sender_name": "Developer Account",
            "recipient": to,
            "snippet": body[:80],
            "body": body,
            "date": "Thu, 28 May 2026 12:00:00 +0000",
            "is_read": True,
            "labels": ["SENT"],
            "ai_category": "Work"
        }
        MOCK_EMAILS.append(new_sent_email)
        return {"message_id": new_sent_email["id"], "status": "sent"}

    service = get_gmail_service(user)
    
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc
    
    message.attach(MIMEText(body, "plain"))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    sent = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    
    return {"message_id": sent.get("id"), "status": "sent"}

def mark_as_read(user: User, email_id: str) -> bool:
    if user.google_id == "mock_dev_user_123":
        for msg in MOCK_EMAILS:
            if msg["id"] == email_id:
                msg["is_read"] = True
                if "UNREAD" in msg["labels"]:
                    msg["labels"].remove("UNREAD")
        return True

    service = get_gmail_service(user)
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
    return True

def trash_email(user: User, email_id: str) -> bool:
    if user.google_id == "mock_dev_user_123":
        for msg in MOCK_EMAILS:
            if msg["id"] == email_id:
                msg["labels"] = ["TRASH"]
        return True

    service = get_gmail_service(user)
    service.users().messages().trash(userId="me", id=email_id).execute()
    return True

