# Ideas Mailer - GitHub Actions

AI-powered daily project ideas by email, plus email-based follow-up replies.
No server, no database, no external hosting required.

This project is designed to run well as a **public GitHub repository** so people can discover it and fork it quickly.

## What It Does

- Sends a daily ideas email using GitHub Models.
- Supports mixed idea types: Web App, Android App, Browser Extension, Electronic.
- Includes project scale and difficulty tags in each card.
- Reads inbound emails and sends AI follow-up replies automatically.

## Workflows

| Workflow | Schedule | Purpose |
|---|---|---|
| `daily-ideas.yml` | `30 2 * * *` (2:30 UTC) | Generate and send daily idea list |
| `reply-checker.yml` | `*/5 * * * *` (every 5 min) | Check inbox and auto-reply to requests |

## Public Repo Note

Keep this repository **Public** if you want maximum visibility and easier forking.
Do not commit secrets. Keep credentials in GitHub Actions secrets only.

## Quick Start

### 1. Fork this repository

1. Click **Fork** (top-right on GitHub).
2. Keep your fork **Public** for discoverability.
3. Open your fork settings and add required secrets.

### 2. Add Actions secrets

Go to **Settings -> Secrets and variables -> Actions -> New repository secret**.

| Secret | Value |
|---|---|
| `GMAIL_USER` | Bot Gmail sender account (example: `bot@gmail.com`) |
| `GMAIL_APP_PASSWORD` | App Password from `GMAIL_USER` account |
| `GMAIL_TO` | Recipient inbox (example: `you@gmail.com`) |
| `MODELS_TOKEN` | GitHub PAT token with Models access |

### 3. Trigger a test run

1. Open **Actions** tab.
2. Run **Daily Project Ideas** workflow manually.
3. Confirm email arrives.

### 4. Test reply flow

1. Send an email from `GMAIL_TO` to `GMAIL_USER`.
2. Example text: `more web app ideas`.
3. Reply checker runs every 5 minutes and responds.

## Example Requests You Can Send by Email

- `more android ideas`
- `more web app ideas`
- `more extension ideas`
- `more hardware ideas`
- `mini project ideas for beginners`
- `tell me more about <project name>`
- `what tech stack for this idea?`

## SEO and Discoverability Tips (GitHub)

To help people find and fork your project:

1. Use this repository description in GitHub About:
   `Daily AI project ideas by email using GitHub Actions, GitHub Models, and Gmail auto-replies.`
2. Add repository topics:
   `github-actions`, `ai`, `project-ideas`, `automation`, `email-automation`, `github-models`, `python`, `gmail`, `productivity`
3. Keep README keywords near top:
   `AI project ideas`, `GitHub Actions automation`, `daily email ideas`, `Gmail auto reply`, `GitHub Models`
4. Keep the repo public and pin it on your profile.

## Repository Structure

```text
.github/
  workflows/
    daily-ideas.yml
    reply-checker.yml
scripts/
  generate_ideas.py
  check_replies.py
.gitignore
README.md
```

## Schedule Customization

GitHub cron uses UTC.

```yaml
# 8:00 AM IST
- cron: '30 2 * * *'

# 1:30 PM IST
- cron: '0 8 * * *'
```

## Troubleshooting

| Problem | Fix |
|---|---|
| 401 Unauthorized from Models API | Verify `MODELS_TOKEN` is valid and active |
| Gmail login failed | Recreate App Password for `GMAIL_USER` |
| No reply emails | Confirm sender is `GMAIL_TO` and checker is enabled |
| Messages in spam | Mark one message as Not spam and retry |

## License

Use any license you prefer (MIT recommended for easier forking).
