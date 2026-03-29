# Ideas Mailer — GitHub Actions

Sends a daily email of 15 project ideas using the GitHub Models API (free with your GitHub account).
Replies to your emails with focused lists or project deep-dives — no server needed.

---

## How it works

| Workflow | Schedule | What it does |
|---|---|---|
| `daily-ideas.yml` | 8:00 AM UTC (1:30 PM IST) | Generates 15 project ideas via AI, sends HTML email |
| `reply-checker.yml` | every 30 min | Reads your unread self-emails, generates contextual AI reply |

All AI calls go to **GitHub Models API** — already included free with your GitHub account.
Emails are sent and read via **Gmail App Password** — no OAuth setup needed.

---

## One-time setup

### 1. Create a Gmail App Password

You need a Gmail App Password (not your regular password) to let the workflow send and read email.

1. Go to [Google Account → Security → 2-Step Verification](https://myaccount.google.com/security) — enable it if not already on
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Choose **Other (Custom name)** → type `ideas-mailer` → click **Generate**
4. Copy the 16-character password shown — you'll add it as a secret next

### 2. Create a GitHub repo and push this code

```bash
cd ideas-mailer
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USERNAME/ideas-mailer.git
git push -u origin main
```

### 3. Add repository secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `GMAIL_USER` | your Gmail address, e.g. `you@gmail.com` |
| `GMAIL_APP_PASSWORD` | the 16-char App Password from step 1 |

> `GITHUB_TOKEN` is provided automatically by GitHub Actions — do NOT add it manually.

### 4. Enable GitHub Models

GitHub Models must be enabled on your account.
Visit [github.com/marketplace/models](https://github.com/marketplace/models) and make sure you have access.

### 5. Test immediately (without waiting for 8 AM)

1. Go to your repo → **Actions** tab
2. Click **Daily Project Ideas** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Watch the run complete — email should arrive within 1–2 minutes

---

## How to trigger the reply checker

Send an email **to yourself** (your Gmail to your Gmail) with any of these:

```
more android ideas
more web ideas
more hardware ideas
more extension ideas
mini projects only
tell me more about [Project Name from the daily email]
what tech stack would I use for a price tracker app?
```

The reply-checker workflow runs every 30 minutes and will reply with AI-generated content.

> **Tip**: You can also reply directly to the daily ideas email — it works the same way.

---

## Files

```
.github/
  workflows/
    daily-ideas.yml       # Runs at 8 AM UTC daily
    reply-checker.yml     # Runs every 30 minutes
scripts/
  generate_ideas.py       # Generates 15 ideas + sends email
  check_replies.py        # Reads inbox, classifies request, replies
.gitignore
README.md
```

No `pip install` required — uses only Python standard library.

---

## Customising the schedule

Edit the `cron:` line in `daily-ideas.yml`:

```yaml
- cron: '0 3 * * *'   # 3:00 AM UTC = 8:30 AM IST
- cron: '30 2 * * *'  # 2:30 AM UTC = 8:00 AM IST
```

Cron times in GitHub Actions are always **UTC**.
[crontab.guru](https://crontab.guru) is useful for calculating your time zone offset.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Email not arriving | Check Actions tab for workflow errors; verify secrets are set correctly |
| `535 Username and Password not accepted` | App Password was not saved correctly; regenerate it |
| Reply checker not finding your email | Make sure Gmail IMAP is enabled: Gmail Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP |
| Ideas email lands in Spam | Mark it as "Not spam" once; Gmail will learn |
