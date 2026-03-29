#!/usr/bin/env python3
"""
Daily project ideas generator.
Calls GitHub Models API to create 15 diverse project ideas and sends them as a
styled HTML email via Gmail SMTP.
"""

import os
import json
import smtplib
import datetime
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = os.environ["GMAIL_USER"]          # bot sender: chandusurisetty11@gmail.com
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
GMAIL_TO = os.environ["GMAIL_TO"]              # your inbox: chandusurisetty58@gmail.com
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

TODAY = datetime.date.today().strftime("%B %d, %Y")
SUBJECT = f"Daily Project Ideas — {TODAY}"
BOT_MARKER = "<!-- ideas-bot -->"

SYSTEM_PROMPT = """You are a creative project idea generator for a developer who builds:
- Web apps / websites
- Android apps
- Browser extensions (Chrome / Firefox)
- Electronic / hardware projects (Arduino, Raspberry Pi, IoT, etc.)
- Mini projects (1–3 day weekend builds)
- Major projects (multi-week / multi-month)

Generate exactly 15 project ideas. Include a healthy mix of:
- Truly innovative / unexplored concepts
- Existing popular GitHub projects that have clear obvious scope to improve significantly

Return ONLY a JSON array (no markdown, no explanation) with this exact shape:
[
  {
    "name": "Project Name",
    "type": "Web App",
    "scale": "Mini",
    "description": "2-3 sentences describing what it does and what makes it interesting.",
    "angle": "The innovative twist or improvement opportunity in one sentence.",
    "tech": "React, Node.js, MongoDB",
    "difficulty": "Easy"
  }
]

type must be one of: Web App, Android App, Browser Extension, Electronic
scale must be one of: Mini, Major  (Mini = 1-3 day build, Major = multi-week build)
difficulty must be one of: Easy, Medium, Hard
tech must be a short comma-separated list of the main languages, frameworks, or hardware (2-4 items max)
"""


def call_github_models(prompt: str) -> str:
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.9,
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


def parse_ideas(raw: str) -> list:
    raw = raw.strip()
    # Strip markdown code fences if the model wrapped the output
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])
        if raw.endswith("```"):
            raw = raw[: raw.rfind("```")]
    # Find first '[' and last ']' to be safe
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON array found in model output:\n{raw[:300]}")
    return json.loads(raw[start:end])


def build_html(ideas: list) -> str:
    type_color = {
        "Web App": "#4f46e5",
        "Android App": "#16a34a",
        "Browser Extension": "#b45309",
        "Electronic": "#dc2626",
        "Mini Project": "#0891b2",
        "Major Project": "#7c3aed",
    }
    diff_color = {"Easy": "#16a34a", "Medium": "#b45309", "Hard": "#dc2626"}
    scale_color = {"Mini": "#0891b2", "Major": "#7c3aed"}

    cards = ""
    for i, idea in enumerate(ideas, 1):
        t = idea.get("type", "")
        d = idea.get("difficulty", "")
        s = idea.get("scale", "")
        tech = idea.get("tech", "")
        tc = type_color.get(t, "#6b7280")
        dc = diff_color.get(d, "#6b7280")
        sc = scale_color.get(s, "#6b7280")
        # Build individual tech tags
        tag_style = (
            'display:inline-block;padding:2px 8px;margin:2px 3px 2px 0;'
            'border-radius:10px;font-size:11px;font-weight:500;'
            'background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;'
        )
        tech_tags = "".join(
            f'<span style="{tag_style}">{tag.strip()}</span>'
            for tag in tech.split(",") if tag.strip()
        )
        cards += f"""
    <div style="background:#fff;border-radius:12px;padding:20px;margin-bottom:14px;
                box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:4px solid {tc};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;
                  flex-wrap:wrap;gap:6px;margin-bottom:10px;">
        <span style="font-size:16px;font-weight:700;color:#111;">{i}. {idea.get('name','')}</span>
      </div>
      <p style="margin:0 0 8px;color:#374151;line-height:1.65;font-size:14px;">
        {idea.get('description','')}
      </p>
      <p style="margin:0 0 12px;color:#6b7280;font-style:italic;font-size:13px;">
        💡 {idea.get('angle','')}
      </p>
      <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;">
        <span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;
                     color:#fff;background:{tc};">{t}</span>
        <span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;
                     color:#fff;background:{sc};">{s} Project</span>
        <span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;
                     color:#fff;background:{dc};">{d}</span>
        <span style="color:#cbd5e1;font-size:11px;">|</span>
        {tech_tags}
      </div>
    </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:700px;margin:0 auto;padding:24px 16px;">

    <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);border-radius:16px;
                padding:28px 32px;margin-bottom:24px;color:#fff;">
      <h1 style="margin:0 0 6px;font-size:24px;">🚀 Daily Project Ideas</h1>
      <p style="margin:0;opacity:.85;">{TODAY} &nbsp;·&nbsp; 15 handpicked ideas</p>
    </div>

    {cards}

    <div style="background:#1e1b4b;border-radius:12px;padding:20px 24px;
                color:#c7d2fe;font-size:13px;margin-top:8px;">
      <p style="margin:0 0 10px;font-weight:600;color:#fff;">
        💬 Want more? Reply to this email with any of these:
      </p>
      <ul style="margin:0;padding-left:18px;line-height:2.2;">
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">more android ideas</code></li>
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">more web ideas</code></li>
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">more hardware ideas</code></li>
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">more extension ideas</code></li>
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">mini projects only</code></li>
        <li><code style="background:#312e81;padding:1px 6px;border-radius:4px;">tell me more about [Project Name]</code></li>
      </ul>
      <p style="margin:10px 0 0;font-size:11px;opacity:.55;">
        Reply checker runs every 30 min · You can also send a new email to yourself with your request
      </p>
    </div>

  </div>
  {BOT_MARKER}
</body>
</html>"""


def send_email(subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_TO
    msg["X-Bot-Generated"] = "true"
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, GMAIL_TO, msg.as_string())
        print("Email sent.")


def main() -> None:
    print(f"Generating ideas for {TODAY} …")
    raw = call_github_models("Generate 15 diverse and interesting project ideas for today.")
    ideas = parse_ideas(raw)
    print(f"Parsed {len(ideas)} ideas.")

    # Use exactly one model request per daily run.
    # If the model returns fewer than 15, we send what we got.
    if len(ideas) > 15:
        ideas = ideas[:15]
        print("Trimmed to 15 ideas.")

    html = build_html(ideas)
    send_email(SUBJECT, html)


if __name__ == "__main__":
    main()
