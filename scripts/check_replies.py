#!/usr/bin/env python3
"""
Reply checker.
Reads unread emails from the user's own inbox (sent-to-self pattern),
skips bot-generated emails, and responds with AI-generated content:
  - "more X ideas" → generates a focused idea list
  - "tell me about X" / questions → gives a detailed breakdown
"""

import os
import re
import json
import imaplib
import smtplib
import email
import email.header
import datetime
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = os.environ["GMAIL_USER"]          # bot account: chandusurisetty11@gmail.com
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
GMAIL_TO = os.environ["GMAIL_TO"]              # your inbox: chandusurisetty58@gmail.com
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

TODAY = datetime.date.today().strftime("%B %d, %Y")
BOT_MARKER = "<!-- ideas-bot -->"

# ── Prompts ─────────────────────────────────────────────────────────────────

IDEAS_SYSTEM = """You are a creative project idea generator.
The user wants a focused list of project ideas matching their specific request.

Generate 10–15 ideas. Use this markdown format for each idea:

**[Number]. [Project Name]** · *[Type]* · *[Difficulty]*
[2-3 sentences: what it does, what makes it interesting or improvable.]
💡 [Innovation angle / improvement opportunity]

---

Types: Web App | Android App | Browser Extension | Electronic | Mini Project | Major Project
Difficulty: Easy | Medium | Hard

Keep ideas practical and genuinely interesting. Vary difficulty unless user specified one."""

DETAIL_SYSTEM = """You are a senior software developer helping someone understand a project idea in depth.

Provide a thorough breakdown including:
1. **What it is** — clear description
2. **Core features** — 4-6 key features
3. **Tech stack** — recommended languages, frameworks, tools
4. **Key challenges** — 2-3 things that make it non-trivial
5. **Monetization / use case** — how it could be useful or profitable
6. **Similar projects** — 2-3 existing GitHub projects or tools to study
7. **MVP scope** — what a minimum viable version looks like

Be concrete, practical, and concise. Use markdown formatting."""

QUESTION_SYSTEM = """You are a knowledgeable developer assistant.
Answer the user's question about software projects clearly and practically.
Keep response under 400 words. Use bullet points or numbered lists where helpful."""


# ── Helpers ──────────────────────────────────────────────────────────────────

def decode_header(value: str) -> str:
    parts = email.header.decode_header(value or "")
    result = []
    for chunk, charset in parts:
        if isinstance(chunk, bytes):
            result.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(chunk)
    return "".join(result)


def get_body(msg) -> str:
    """Extract the best available text body from a parsed email."""
    plain = ""
    html = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if "attachment" in cd:
                continue
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                text = payload.decode("utf-8", errors="replace")
                if ct == "text/plain" and not plain:
                    plain = text
                elif ct == "text/html" and not html:
                    html = text
            except Exception:
                continue
    else:
        try:
            plain = (msg.get_payload(decode=True) or b"").decode("utf-8", errors="replace")
        except Exception:
            pass
    return plain or html


def call_github_models(system: str, user_message: str) -> str:
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 3000,
        "temperature": 0.85,
    }).encode()

    req = urllib.request.Request(
        "https://models.inference.ai.azure.com/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML for the AI's response."""
    # Escape bare HTML chars that could exist in project names
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r'<code style="background:#f1f5f9;padding:1px 5px;border-radius:3px;">\1</code>', text)
    # Horizontal rule
    text = re.sub(r"^---+$", '<hr style="border:none;border-top:1px solid #e5e7eb;margin:14px 0;">', text, flags=re.MULTILINE)

    lines = text.split("\n")
    html_lines: list[str] = []
    in_ul = False

    for line in lines:
        stripped = line.rstrip()

        # Numbered bold heading pattern: "**1. Title**" on its own line
        if re.match(r"^\d+\.", stripped) and stripped.startswith("<strong>"):
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append(
                f'<p style="margin:14px 0 4px;font-size:15px;color:#111;">{stripped}</p>'
            )
            continue

        # Bullet point
        if re.match(r"^[-•]\s+", stripped):
            if not in_ul:
                html_lines.append('<ul style="margin:6px 0 6px 16px;padding:0;">')
                in_ul = True
            item = re.sub(r"^[-•]\s+", "", stripped)
            html_lines.append(
                f'<li style="margin-bottom:5px;color:#374151;line-height:1.6;">{item}</li>'
            )
            continue

        if in_ul:
            html_lines.append("</ul>")
            in_ul = False

        if stripped:
            html_lines.append(
                f'<p style="margin:8px 0;color:#374151;line-height:1.7;">{stripped}</p>'
            )
        else:
            html_lines.append('<div style="height:6px;"></div>')

    if in_ul:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def build_reply_html(ai_response: str, request_preview: str) -> str:
    content = md_to_html(ai_response)
    safe_request = request_preview[:300].replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:700px;margin:0 auto;padding:24px 16px;">

    <div style="background:linear-gradient(135deg,#0891b2,#4f46e5);border-radius:16px;
                padding:24px 28px;margin-bottom:20px;color:#fff;">
      <h1 style="margin:0 0 4px;font-size:21px;">💬 Reply to Your Request</h1>
      <p style="margin:0;opacity:.8;font-size:13px;">{TODAY}</p>
    </div>

    <div style="background:#f0f9ff;border-left:4px solid #0891b2;padding:12px 16px;
                border-radius:8px;margin-bottom:20px;color:#0369a1;font-size:13px;">
      <strong>Your request:</strong> {safe_request}
    </div>

    <div style="background:#fff;border-radius:12px;padding:24px 28px;
                box-shadow:0 1px 4px rgba(0,0,0,.08);">
      {content}
    </div>

    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">
      Reply again to ask a follow-up &nbsp;·&nbsp; Checker runs every 30 min
    </p>

  </div>
  {BOT_MARKER}
</body>
</html>"""


def classify_request(subject: str, body: str) -> str:
    """
    Returns one of: 'ideas', 'detail', 'question'
    """
    text = (subject + " " + body[:500]).lower()

    idea_keywords = [
        "more", "give me", "send me", "suggest", "ideas", "projects",
        "android", "web", "hardware", "extension", "mini", "major",
        "electronic", "only", "list",
    ]
    detail_keywords = [
        "tell me more about", "explain", "breakdown", "details about",
        "how would i build", "tech stack for", "more about",
    ]

    if any(k in text for k in detail_keywords):
        return "detail"
    if any(k in text for k in idea_keywords):
        return "ideas"
    return "question"


def is_bot_email(msg, body: str) -> bool:
    return BOT_MARKER in body or msg.get("X-Bot-Generated", "") == "true"


def send_reply(original_msg, html: str, original_subject: str) -> None:
    reply_subject = (
        original_subject if original_subject.startswith("Re:")
        else f"Re: {original_subject}"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = reply_subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_TO
    msg["X-Bot-Generated"] = "true"

    # Thread correctly
    msg_id = original_msg.get("Message-ID", "")
    if msg_id:
        msg["In-Reply-To"] = msg_id
        msg["References"] = msg_id

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, GMAIL_TO, msg.as_string())


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Connecting to Gmail IMAP …")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    imap.select("INBOX")

    # Find unread emails from the user's personal address (replies to the bot)
    _, data = imap.search(None, f'(UNSEEN FROM "{GMAIL_TO}")')
    email_ids = data[0].split()

    if not email_ids:
        print("No unread self-emails found.")
        imap.logout()
        return

    print(f"Found {len(email_ids)} unread email(s) from self.")
    processed = 0

    for eid in email_ids:
        _, msg_data = imap.fetch(eid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = decode_header(msg.get("Subject", "(no subject)"))
        body = get_body(msg)

        # Always mark as read so bot-generated emails are never re-checked
        imap.store(eid, "+FLAGS", "\\Seen")

        if is_bot_email(msg, body):
            print(f"  skip (bot): {subject}")
            continue

        print(f"  processing: {subject}")
        request_text = body.strip()[:1500] or subject

        intent = classify_request(subject, body)

        if intent == "ideas":
            system = IDEAS_SYSTEM
            prompt = f"User request: {request_text}\n\nGenerate focused project ideas matching this request."
        elif intent == "detail":
            system = DETAIL_SYSTEM
            prompt = f"User wants details about a project. Their message:\n{request_text}"
        else:
            system = QUESTION_SYSTEM
            prompt = request_text

        try:
            answer = call_github_models(system, prompt)
            reply_html = build_reply_html(answer, request_text)
            send_reply(msg, reply_html, subject)
            print(f"  replied to: {subject}")
            processed += 1
        except Exception as exc:
            print(f"  error for '{subject}': {exc}")

    imap.logout()
    print(f"Done — processed {processed} email(s).")


if __name__ == "__main__":
    main()
