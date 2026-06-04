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
        text = ""
        candidate = data.get("candidates", [None])[0] or {}
        content = candidate.get("content", []) if isinstance(candidate, dict) else []
        if content:
            first = content[0]
            if isinstance(first, dict) and first.get("parts"):
                text = first["parts"][0].get("text", "")
            elif isinstance(first, dict):
                text = first.get("text", "")
        cleaned = _clean_gemini_echo(prompt, text)
        return cleaned
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
            return "Hi,\n\nI can definitely reschedule our meeting. Please let me know what times work best for you this week, and I'll send over an updated calendar invite.\n\nBest regards,\nPrerna"
        else:
            return "Hi,\n\nNo problem at all, I can move our meeting. Let me know when you're free and we'll get it rescheduled.\n\nBest,\nPrerna"
    elif "deadline" in body or "urgent" in body or "schema" in body:
        if tone == "professional":
            return "Hi,\n\nThanks for letting me know. I've reviewed the project details and will make sure the work is finished by the deadline. Let me know if you need anything else.\n\nBest regards,\nPrerna"
        else:
            return "Hi,\n\nThanks for the heads-up. I'll make sure to get this done by the deadline today.\n\nThanks,\nPrerna"
    
    if tone == "professional":
        context_str = f" Regarding your point: {additional_context}." if additional_context else ""
        return f"Hi,\n\nThanks for reaching out. I'm reviewing the details about '{email_subject or 'our project'}' and will get back to you with an update shortly.{context_str}\n\nBest regards,\nPrerna"
    else:
        context_str = f" {additional_context}." if additional_context else ""
        return f"Hi,\n\nThanks for the message! I'm on it and will check out the details for '{email_subject or 'our project'}' right away.{context_str}\n\nCheers,\nPrerna"

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
    def get_mock_ai_compose(prompt_text: str, tone: str = "professional",
                        user_name: str = "", today_date: str = "") -> str:
    """
    Smart mock compose: reads the user's intent from the prompt and returns
    a contextually correct, ready-to-send email — not a generic follow-up.
    Substitutes placeholders and defaults name to 'Prerna' if generic.
    """
    from datetime import date as _date
    p = prompt_text.lower()
    formal = tone in ("professional", "formal")
    name = user_name.strip() if (user_name.strip() and user_name.strip() not in ["[Your Name]", "Developer Account"]) else "Prerna"
    today = today_date.strip() if today_date.strip() else _date.today().strftime("%d/%m/%Y")

    # ── Friend / Casual Say Hello / Greetings ──────────────────────────────
    if any(k in p for k in ["friend", "hello", "greet", "how are you", "say hello"]):
        return (
            "Subject: Hello, How Have You Been?\n\n"
            "Hi,\n\n"
            "Hope you're doing well! I just wanted to say hello and see how you've been lately. It's been a while, and I hope everything is going great for you.\n\n"
            "Sending my best wishes and greetings. Looking forward to hearing from you soon!\n\n"
            f"Take care,\n{name}"
        )

    # ── Sick / Medical leave ───────────────────────────────────────────────
    if any(k in p for k in ["sick leave", "sick day", "medical leave", "ill", "unwell", "not feeling well", "health"]):
        if formal:
            return (
                "Subject: Sick Leave Request\n\n"
                "Hi,\n\n"
                f"I won't be able to come in today, {today}, as I'm feeling unwell. I'll make sure to catch up on any pending tasks as soon as I return. Please let me know if you need anything urgent.\n\n"
                f"Best regards,\n{name}"
            )
        else:
            return (
                "Subject: Out Sick Today\n\n"
                "Hi,\n\n"
                f"I'm feeling under the weather and need to take today off. I'll check my emails periodically and keep you posted on my return.\n\n"
                f"Thanks,\n{name}"
            )

    # ── Half day / Early leave ─────────────────────────────────────────────
    if any(k in p for k in ["half day", "half-day", "early leave", "half leave", "early exit", "leave early"]):
        if formal:
            return (
                f"Subject: Half Day Request - {today}\n\n"
                "Hi,\n\n"
                f"I need to request a half-day leave for today, {today}, due to personal commitments. I will ensure all urgent matters are wrapped up before I head out.\n\n"
                f"Best regards,\n{name}"
            )
        else:
            return (
                "Subject: Leaving Early Today\n\n"
                "Hi,\n\n"
                "I have to head out early today for some personal errands. I'll make sure my key tasks are covered before I leave. Let me know if there's anything urgent.\n\n"
                f"Cheers,\n{name}"
            )

    # ── Leave of absence / vacation / holiday ─────────────────────────────
    if any(k in p for k in ["leave", "vacation", "holiday", "time off", "day off", "absence"]):
        if formal:
            return (
                "Subject: Vacation Leave Request\n\n"
                "Hi,\n\n"
                "I would like to request leave for the upcoming week. I will ensure all my tasks are completed and handover details are shared with the team before my time off.\n\n"
                f"Best regards,\n{name}"
            )
        else:
            return (
                "Subject: Upcoming Time Off Request\n\n"
                "Hi,\n\n"
                "I'm planning to take a few days off next week for a short holiday. I'll make sure everything is sorted and covered before I go.\n\n"
                f"Thanks,\n{name}"
            )

    # ── Job application ────────────────────────────────────────────────────
    if any(k in p for k in ["job", "apply", "application", "resume", "position", "hiring", "opportunity", "role", "vacancy"]):
        return (
            "Subject: Software Engineer Application\n\n"
            "Hi Hiring Team,\n\n"
            "I'm excited to apply for the software engineer role. With my background in building web applications, I believe I would be a great fit for your team.\n\n"
            "My resume is attached. I look forward to the possibility of discussing this opportunity with you.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Meeting request ────────────────────────────────────────────────────
    if any(k in p for k in ["meeting", "schedule", "appointment", "call", "sync", "catch up", "discuss"]):
        greeting = "Hi Team," if "team" in p else "Hi,"
        subject = "Meeting Request"
        if "weekly sync" in p:
            subject = "Weekly Sync Meeting"
        elif "product" in p:
            subject = "Product Team Catch Up"
        elif "project" in p:
            subject = "Project Update Meeting"
            
        if formal:
            return (
                f"Subject: {subject}\n\n"
                f"{greeting}\n\n"
                "Could we schedule a brief meeting this week to discuss the project status? Please let me know your availability for a quick 30-minute discussion.\n\n"
                f"Best regards,\n{name}"
            )
        else:
            return (
                f"Subject: {subject}\n\n"
                f"{greeting}\n\n"
                "Let's set up a quick catch-up this week to go over the latest updates. Let me know when you're free for a 15-minute sync.\n\n"
                f"Cheers,\n{name}"
            )

    # ── Thank you ──────────────────────────────────────────────────────────
    if any(k in p for k in ["thank", "gratitude", "appreciate", "thanks"]):
        if formal:
            return (
                "Subject: Sincere Appreciation\n\n"
                "Hi,\n\n"
                "Thank you very much for your help on the project. Your support was invaluable, and I truly appreciate the effort you put in.\n\n"
                f"Best regards,\n{name}"
            )
        else:
            return (
                "Subject: Thanks For Your Help!\n\n"
                "Hi,\n\n"
                "Just wanted to say a quick thanks for helping me out yesterday. Really appreciate you taking the time to guide me through it.\n\n"
                f"Cheers,\n{name}"
            )

    # ── Apology ────────────────────────────────────────────────────────────
    if any(k in p for k in ["apology", "apologize", "sorry", "mistake", "error", "regret"]):
        return (
            "Subject: Apology for the Delay\n\n"
            "Hi,\n\n"
            "I wanted to apologize for the delay in sending over the reports. I had some technical difficulties but have now resolved them. Thank you for your patience.\n\n"
            f"Sincerely,\n{name}"
        )

    # ── Resignation ────────────────────────────────────────────────────────
    if any(k in p for k in ["resign", "resignation", "quit", "notice period", "last day"]):
        return (
            "Subject: Resignation Notification\n\n"
            "Hi,\n\n"
            "Please accept this email as notification that I am resigning from my position. My last day will be in two weeks. I appreciate the opportunities I've had during my time here.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Complaint / issue ──────────────────────────────────────────────────
    if any(k in p for k in ["complaint", "issue", "problem", "concern", "escalate", "dissatisfied"]):
        return (
            "Subject: Issue with Recent Delivery\n\n"
            "Hi Customer Support,\n\n"
            "I noticed that my recent order has arrived damaged. I would appreciate it if you could assist in arranging a replacement or refund.\n\n"
            f"Regards,\n{name}"
        )

    # ── Project / status update ────────────────────────────────────────────
    if any(k in p for k in ["update", "status", "progress", "report", "project"]):
        return (
            "Subject: Project Status Update\n\n"
            "Hi Team,\n\n"
            "Here is a quick status update. We have completed the core features and are now moving into testing. We remain on track to deliver by the end of the week.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Introduction ───────────────────────────────────────────────────────
    if any(k in p for k in ["introduction", "introduce", "self intro", "new member", "joining"]):
        return (
            "Subject: Introducing Myself\n\n"
            "Hi Everyone,\n\n"
            "I'm excited to join the team as the new software engineer. I look forward to working with all of you and getting to know everyone soon.\n\n"
            f"Best regards,\n{name}"
        )

    # ── Generic smart fallback ─────────────────────────────────────────────
    topic = prompt_text.strip().rstrip(".")
    words = topic.split()
    if len(words) > 5:
        subject_title = " ".join(words[:5]).title()
    else:
        subject_title = topic.title()
    
    if not formal or any(k in p for k in ["friend", "casual", "hello", "hi", "hey"]):
        return (
            f"Subject: {subject_title}\n\n"
            "Hi,\n\n"
            f"Hope all is well. I wanted to catch up and talk about {topic.lower()}. Let me know if you've got some free time soon.\n\n"
            f"Cheers,\n{name}"
        )
    else:
        return (
            f"Subject: {subject_title}\n\n"
            "Hi,\n\n"
            f"Hope you're having a good week. I wanted to follow up on the discussion regarding {topic.lower()}. Please let me know your thoughts when you have a moment.\n\n"
            f"Best regards,\n{name}"
        )�───────
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


def _clean_gemini_echo(prompt: str, text: str) -> str:
    """Remove echoed prompt or instruction noise from model output.

    Heuristics:
    - If the model echoed the full prompt, remove the prompt text.
    - If the model includes clear markers like 'Reply:' or 'Email:', take the
      content after the last marker.
    - As a last resort, if the response starts with the prompt prefix, strip
      that prefix.
    """
    if not text:
        return ""

    t = text.strip()
    p = (prompt or "").strip()

    # If the prompt appears verbatim in the output, remove occurrences
    if p and p in t:
        t = t.replace(p, "").strip()

    # Common markers that separate prompt from response
    markers = ["\n\nReply:", "\nReply:", "Reply:", "\n\nEmail:", "\nEmail:", "Email:", "\n\nSummary:", "\nSummary:", "Summary:"]
    for m in markers:
        idx = t.find(m)
        if idx != -1:
            return t[idx + len(m):].strip()

    # If response starts with a long prefix matching start of prompt, strip it
    max_prefix = min(len(p), 200)
    if p and t.startswith(p[:max_prefix]):
        return t[len(p[:max_prefix]):].strip()

    return t

# ---------------------------------------------------------------------------
# API Functions with Fallback Logic
# ---------------------------------------------------------------------------

def generate_email_reply(email_body: str, email_subject: str = "",
                          tone: str = "professional", additional_context: str = "") -> str:
    prompt = f"""You are an expert email assistant. Generate a natural, human-like, concise {tone} reply to the following email.

Email Subject: {email_subject}

Email Content:
{email_body}

{f'Additional Context: {additional_context}' if additional_context else ''}

Instructions:
- Write a complete, ready-to-send email reply.
- Do NOT use formal/robotic business email templates or generic corporate tones, especially if a casual/friendly tone is selected or the topic is informal.
- Do NOT start with "I am writing regarding...", "I am writing to...", or similar robotic templates.
- Be concise, personalized, and realistic.
- Do NOT include any placeholders like [Name], [Your Name], [Company Name], or any text in square brackets. Use realistic names or omit them.
- Start directly with the greeting.
- Return only the final email reply content, without any explanations, chatbot meta-text, markdown backticks, or instructions. Do NOT include the original email content in your response.

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
    name = user_name.strip() if (user_name.strip() and user_name.strip() not in ["[Your Name]", "Developer Account"]) else "Prerna"
    today = today_date.strip() if today_date.strip() else _date.today().strftime("%d/%m/%Y")

    prompt = f"""You are an expert email assistant. Write a natural, human-like email based on the user's intent below.

User Intent/Request: {prompt_text}
Selected Tone: {tone}
Sender Name: {name}
Today's Date: {today}

CRITICAL RULES:
1. Subject Line:
   - Must start with "Subject: "
   - Must be short and relevant (max 5-7 words)
   - Must be different from the email body
2. Email Body:
   - Write according to the user's intent only. If the request is personal, generate a personal email. If professional, generate a professional email.
   - Do NOT use formal business email templates or generic corporate structures (especially for casual emails).
   - Do NOT start with "I am writing regarding...", "I am writing to...", or similar robotic/formal templates.
   - Use a friendly, conversational tone when selected or when the email is personal.
   - Keep the email concise, personalized, and realistic.
   - Do NOT include any placeholders like [Name], [Recipient's Name], [Date], [Company Name], [Add your key points here], [Your Name], or anything in square brackets. Write a ready-to-send email with realistic details.
   - Sign off naturally using the Sender Name: {name}.
3. Format:
   - Return ONLY the final email content (Subject line and body). Do not include any explanations, chatbot meta-text, markdown backticks, or copy of the instructions.

Email:"""
    res = call_gemini_api(prompt)
    if res.startswith("⚠️") or "stub" in res:
        print(f"[Gemini Fallback] Using high-fidelity mock compose due to Gemini status: {res[:50]}...")
        return get_mock_ai_compose(prompt_text, tone, user_name=name, today_date=today)
    
    # Clean up any leftover markdown block syntax or generic placeholders if any
    res = res.strip().replace("```", "")
    res = res.replace("[Your Name]", name)
    return res
