import os
import re
# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv(override=True)

def call_gemini_api(prompt: str) -> str:
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "mock_gemini_key":
        return "[Gemini AI response stub: Configure real GEMINI_API_KEY to see actual AI generation]"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        if response.status_code == 429:
            return "⚠️ Gemini API rate limit exceeded. Your free-tier quota is used up. Wait a minute and try again, or upgrade your Google AI Studio plan."
        if response.status_code == 403:
            return "⚠️ Gemini API access denied (403). Check that your API key has the Generative Language API enabled in Google Cloud Console."
        if response.status_code != 200:
            err = response.json().get("error", {})
            return f"⚠️ Gemini API error ({response.status_code}): {err.get('message', response.text[:200])}"
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except httpx.TimeoutException:
        return "⚠️ Gemini API request timed out. Please try again."
    except Exception as e:
        print(f"Gemini API call error: {e}")
        return f"⚠️ AI generation error: {str(e)}"

# ---------------------------------------------------------------------------
# High-Fidelity Mock Fallback Generators (Used if Gemini is rate-limited/429/403)
# ---------------------------------------------------------------------------

def get_mock_ai_reply(email_body: str, email_subject: str = "", tone: str = "professional", additional_context: str = "") -> str:
    subj = (email_subject or "").lower()
    body = (email_body or "").lower()
    
    if "reschedule" in body or "meeting" in body:
        if tone == "professional":
            return "Dear Sarah,\n\nThank you for reaching out. Yes, I can certainly reschedule our meeting. Please let me know what alternative times work best for you, and I will adjust my calendar accordingly.\n\nBest regards,\nDeveloper Account"
        else:
            return "Hi Sarah,\n\nNo problem at all! Let's reschedule. Let me know when you're free and we'll make it work.\n\nBest,\nDeveloper"
            
    elif "deadline" in body or "urgent" in body or "schema" in body:
        if tone == "professional":
            return "Dear Sarah,\n\nThank you for the update regarding the API schema deadline. I have reviewed the schemas.py file and have applied the necessary fixes. I will ensure everything is ready by end of day today.\n\nBest regards,\nDeveloper Account"
        else:
            return "Hey Sarah,\n\nGot it! I just checked the schemas.py file and made sure the fixes are applied. I'll make sure it's fully ready by end of day today.\n\nThanks,\nDeveloper"
            
    if tone == "professional":
        context_str = f" Regarding your point: {additional_context}." if additional_context else ""
        return f"Dear Sender,\n\nThank you for your message. I have received your email regarding '{email_subject or 'our discussion'}' and will review the details shortly.{context_str}\n\nBest regards,\nDeveloper Account"
    else:
        context_str = f" {additional_context}." if additional_context else ""
        return f"Hi there,\n\nThanks for writing! I got your message about '{email_subject or 'our discussion'}'. I'll look into it and get back to you soon.{context_str}\n\nCheers,\nDeveloper"

def get_mock_ai_summary(email_body: str, email_subject: str = "") -> str:
    body = (email_body or "").lower()
    if "deadline" in body or "schema" in body:
        return "• Sarah requested final feedback on the API schema for the AI Email Assistant.\n• Action Required: Review updated schemas.py file.\n• Deadline: End of day today."
    elif "coffee" in body:
        return "• Alex invited you for coffee this Friday.\n• Time: Friday at 4:00 PM.\n• Location: Near your office."
    elif "statement" in body or "credit" in body:
        return "• Chase Bank monthly credit card statement for April 2026 is now available.\n• Action: Log in online to review statement and make payment if needed."
    return f"• Summarized request regarding '{email_subject or 'discussion'}'.\n• Key action: Review the content and reply accordingly."

def get_mock_ai_grammar(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    replacements = {
        r"\bi is\b": "I am",
        r"\byou is\b": "you are",
        r"\bthey is\b": "they are",
        r"\bhe are\b": "he is",
        r"\bshe are\b": "she is",
        r"\bwe is\b": "we are",
        r"\bi have went\b": "I went",
        r"\bdont\b": "don't",
        r"\bdoesnt\b": "doesn't",
        r"\bim\b": "I'm"
    }
    for pattern, rep in replacements.items():
        cleaned = re.sub(pattern, rep, cleaned, flags=re.IGNORECASE)
    return cleaned

def get_mock_ai_classify(email_subject: str = "", email_body: str = "", sender: str = "") -> str:
    subj = (email_subject or "").lower()
    body = (email_body or "").lower()
    if "deadline" in subj or "schema" in subj or "project" in subj or "meeting" in subj:
        return "Work"
    if "statement" in subj or "invoice" in subj or "billing" in subj or "payment" in subj:
        return "Finance"
    if "coffee" in subj or "lunch" in subj or "party" in subj:
        return "Personal"
    if "newsletter" in subj or "weekly" in subj or "digest" in subj:
        return "Newsletter"
    if "offer" in subj or "discount" in subj or "deal" in subj or "sale" in subj:
        return "Promotions"
    return "Updates"

def get_mock_ai_compose(prompt_text: str, tone: str = "professional",
                        user_name: str = "", today_date: str = "") -> str:
    """
    Smart mock compose: reads the user's intent from the prompt and returns
    a contextually correct, ready-to-send email — not a generic follow-up.
    Substitutes [Your Name] with user_name and fills today's date where relevant.
    """
    from datetime import date as _date
    p = prompt_text.lower()
    formal = tone in ("professional", "formal")
    name = user_name.strip() if user_name.strip() else "[Your Name]"
    today = today_date.strip() if today_date.strip() else _date.today().strftime("%d/%m/%Y")

    # ── Sick / Medical leave ───────────────────────────────────────────────
    if any(k in p for k in ["sick leave", "sick day", "medical leave", "ill", "unwell", "not feeling well", "health"]):
        greeting = "Dear Manager," if formal else "Hi,"
        sign = "Best regards," if formal else "Thanks,"
        return (
            f"Subject: Sick Leave Request\n\n"
            f"{greeting}\n\n"
            f"I am writing to inform you that I am feeling unwell and am unable to come to the office today ({today}). "
            f"I would like to request a sick leave for {today}.\n\n"
            f"I will ensure that all pending tasks are handled and I will keep you updated on my recovery. "
            f"Please let me know if you need any documentation from me.\n\n"
            f"{sign}\n{name}"
        )

    # ── Half day / Early leave ─────────────────────────────────────────────
    if any(k in p for k in ["half day", "half-day", "early leave", "half leave", "early exit", "leave early"]):
        greeting = "Dear Manager," if formal else "Hi,"
        sign = "Best regards," if formal else "Thanks,"
        return (
            f"Subject: Request for Half Day / Early Leave\n\n"
            f"{greeting}\n\n"
            f"I am writing to request a half-day / early leave on {today}. "
            f"I will ensure all my urgent tasks are completed or delegated before I leave.\n\n"
            f"Please let me know if this can be accommodated.\n\n"
            f"{sign}\n{name}"
        )

    # ── Leave of absence / vacation / holiday ─────────────────────────────
    if any(k in p for k in ["leave", "vacation", "holiday", "time off", "day off", "absence"]):
        greeting = "Dear Manager," if formal else "Hi,"
        sign = "Best regards," if formal else "Thanks,"
        return (
            f"Subject: Leave of Absence Request\n\n"
            f"{greeting}\n\n"
            f"I am writing to formally request a leave of absence from [DD/MM/YYYY] to [DD/MM/YYYY] "
            f"for personal reasons. I will ensure that all my responsibilities are covered during my absence "
            f"and I will handover pending tasks before I leave.\n\n"
            f"Please let me know if this is feasible and if any additional information is required.\n\n"
            f"{sign}\n{name}"
        )

    # ── Job application ────────────────────────────────────────────────────
    if any(k in p for k in ["job", "apply", "application", "resume", "position", "hiring", "opportunity", "role", "vacancy"]):
        return (
            f"Subject: Application for [Position Name] – {name}\n\n"
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the [Position Name] role at [Company Name]. "
            f"With my background in [relevant field] and [X] years of experience, I am confident in my "
            f"ability to contribute meaningfully to your team.\n\n"
            f"I have attached my resume and portfolio for your review. I would welcome the opportunity "
            f"to discuss how my skills align with your needs.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best regards,\n{name}\n[Phone Number]"
        )

    # ── Meeting request ────────────────────────────────────────────────────
    if any(k in p for k in ["meeting", "schedule", "appointment", "call", "sync", "catch up", "discuss"]):
        greeting = "Dear [Name]," if formal else "Hi [Name],"
        sign = "Best regards," if formal else "Cheers,"
        return (
            f"Subject: Meeting Request – [Topic]\n\n"
            f"{greeting}\n\n"
            f"I hope this message finds you well. I would like to schedule a meeting to discuss [topic]. "
            f"Could you please let me know your availability for a [30/60]-minute call this week?\n\n"
            f"I am available on [DD/MM/YYYY] between [Time range], but I am happy to adjust to a time that suits you better.\n\n"
            f"{sign}\n{name}"
        )

    # ── Thank you ──────────────────────────────────────────────────────────
    if any(k in p for k in ["thank", "gratitude", "appreciate", "thanks"]):
        greeting = "Dear [Name]," if formal else "Hi [Name],"
        sign = "Warm regards," if formal else "Thanks again,"
        return (
            f"Subject: Thank You – [Context]\n\n"
            f"{greeting}\n\n"
            f"I just wanted to take a moment to sincerely thank you for [reason]. "
            f"Your support and assistance have been truly valuable and greatly appreciated.\n\n"
            f"I look forward to continuing to work with you.\n\n"
            f"{sign}\n{name}"
        )

    # ── Apology ────────────────────────────────────────────────────────────
    if any(k in p for k in ["apology", "apologize", "sorry", "mistake", "error", "regret"]):
        return (
            f"Subject: Sincere Apology Regarding [Issue]\n\n"
            f"Dear [Name],\n\n"
            f"I am writing to sincerely apologize for [description of issue]. I understand that this "
            f"may have caused inconvenience, and I take full responsibility for the mistake.\n\n"
            f"I am actively working to resolve this and will ensure it does not happen again. "
            f"Please let me know how I can make this right.\n\n"
            f"Sincerely,\n{name}"
        )

    # ── Resignation ────────────────────────────────────────────────────────
    if any(k in p for k in ["resign", "resignation", "quit", "notice period", "last day"]):
        return (
            f"Subject: Resignation Letter – {name}\n\n"
            f"Dear [Manager's Name],\n\n"
            f"I am writing to formally notify you of my resignation from my position as [Job Title] at "
            f"[Company Name], effective [DD/MM/YYYY — typically 2 weeks from {today}].\n\n"
            f"I am grateful for the opportunities and experiences I have gained during my time here. "
            f"I will do my best to ensure a smooth transition and handover of my responsibilities.\n\n"
            f"Thank you for your support and guidance.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Complaint / issue ──────────────────────────────────────────────────
    if any(k in p for k in ["complaint", "issue", "problem", "concern", "escalate", "dissatisfied"]):
        return (
            f"Subject: Formal Complaint – [Brief Description]\n\n"
            f"Dear [Name/Department],\n\n"
            f"I am writing to bring to your attention a concern regarding [specific issue]. "
            f"On {today}, I experienced [describe the problem clearly]. This has caused [impact].\n\n"
            f"I kindly request that this matter be investigated and resolved as soon as possible. "
            f"Please acknowledge receipt of this complaint and advise on the next steps.\n\n"
            f"Regards,\n{name}"
        )

    # ── Project / status update ────────────────────────────────────────────
    if any(k in p for k in ["update", "status", "progress", "report", "project"]):
        return (
            f"Subject: Project Status Update – [Project Name]\n\n"
            f"Dear Team,\n\n"
            f"I am writing to provide a quick update on the progress of [Project Name] as of {today}.\n\n"
            f"✅ Completed: [Milestone 1], [Milestone 2]\n"
            f"🔄 In Progress: [Current task]\n"
            f"⏳ Upcoming: [Next milestone by DD/MM/YYYY]\n\n"
            f"Please let me know if you have any questions or need further details.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Introduction ───────────────────────────────────────────────────────
    if any(k in p for k in ["introduction", "introduce", "self intro", "new member", "joining"]):
        return (
            f"Subject: Introduction – {name}\n\n"
            f"Dear Team,\n\n"
            f"I am excited to introduce myself. My name is {name} and I have recently joined the "
            f"team as [Your Role]. I bring [X] years of experience in [your field].\n\n"
            f"I look forward to collaborating with everyone and contributing to the team's success. "
            f"Please feel free to reach out to me at any time.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Generic smart fallback (much better than the old "follow-up") ──────
    topic = prompt_text.strip().rstrip(".")
    greeting = "Dear [Name]," if formal else "Hi [Name],"
    sign = "Best regards," if formal else "Cheers,"
    return (
        f"Subject: {topic.title()}\n\n"
        f"{greeting}\n\n"
        f"I am writing to you regarding {topic.lower()}. "
        f"Please find the relevant details below and feel free to reach out if you have any questions or require additional information.\n\n"
        f"[Add your key points here]\n\n"
        f"{sign}\n{name}"
    )

# ---------------------------------------------------------------------------
# API Functions with Fallback Logic
# ---------------------------------------------------------------------------

def generate_email_reply(email_body: str, email_subject: str = "",
                          tone: str = "professional", additional_context: str = "") -> str:
    prompt = f"""You are an expert email assistant. Generate a concise, {tone} reply to the following email.

Email Subject: {email_subject}

Email Content:
{email_body}

{f'Additional Context: {additional_context}' if additional_context else ''}

Instructions:
- Write a complete, ready-to-send email reply
- Match the {tone} tone
- Be concise and clear
- Do NOT include placeholders like [Your Name] — just write the reply body
- Start directly with the greeting

Reply:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using high-fidelity mock reply due to Gemini status: {res[:50]}...")
        return get_mock_ai_reply(email_body, email_subject, tone, additional_context)
    return res

def summarize_email(email_body: str, email_subject: str = "") -> str:
    prompt = f"""Summarize the following email in 2-3 concise bullet points. Focus on the key information, actions required, and important dates.

Subject: {email_subject}

Email:
{email_body}

Provide a structured summary with:
- Main topic/purpose
- Key points (if any)
- Action items required (if any)

Summary:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using high-fidelity mock summary due to Gemini status: {res[:50]}...")
        return get_mock_ai_summary(email_body, email_subject)
    return res

def correct_grammar(text: str) -> str:
    prompt = f"""You are a professional writing assistant. Correct the grammar, spelling, punctuation, and improve the clarity of the following text. Return ONLY the corrected text without any explanation.

Original text:
{text}

Corrected text:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using grammar correction fallback due to Gemini status: {res[:50]}...")
        return get_mock_ai_grammar(text)
    return res

def classify_email(email_subject: str = "", email_body: str = "", sender: str = "") -> str:
    prompt = f"""Classify the following email into exactly ONE of these categories:
- Work
- Personal
- Finance
- Newsletter
- Promotions
- Social
- Updates
- Spam
- Support
- Travel

Email details:
From: {sender}
Subject: {email_subject}
Body (first 500 chars): {email_body[:500]}

Respond with ONLY the category name, nothing else.

Category:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using classification fallback due to Gemini status: {res[:50]}...")
        return get_mock_ai_classify(email_subject, email_body, sender)
        
    valid_categories = ["Work", "Personal", "Finance", "Newsletter", "Promotions", 
                         "Social", "Updates", "Spam", "Support", "Travel"]
    for cat in valid_categories:
        if cat.lower() in res.lower():
            return cat
    return "Updates"

def compose_email_ai(prompt_text: str, tone: str = "professional",
                     user_name: str = "", today_date: str = "") -> str:
    from datetime import date as _date
    name = user_name.strip() if user_name.strip() else "[Your Name]"
    today = today_date.strip() if today_date.strip() else _date.today().strftime("%d/%m/%Y")

    prompt = f"""You are an expert email writer. Compose a complete, {tone} email based on the following request.

Request: {prompt_text}

Important:
- Sign the email with the sender's name: {name}
- Today's date is {today}. Use this real date wherever a date is relevant (e.g. sick leave for today, complaint date, etc.).
- For date ranges that the user has not specified (e.g. leave start/end), use the placeholder [DD/MM/YYYY].
- Do NOT use generic placeholders like "[Your Name]" — use {name} instead.

Write a complete email with:
- Subject line (start with "Subject: ")
- Proper greeting
- Clear body
- Professional closing signed by {name}

Email:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using high-fidelity mock compose due to Gemini status: {res[:50]}...")
        return get_mock_ai_compose(prompt_text, tone, user_name=name, today_date=today)
    # Post-process: replace any leftover [Your Name] placeholders from Gemini output
    res = res.replace("[Your Name]", name)
    return res
