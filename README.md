# 📬 Email SaaS Scheduler

A full-featured, multi-tenant email automation system built with FastAPI, supporting intelligent sequences, working-hour delivery, per-user SMTP, throttling, and retry logic. Designed for deployment on local servers or cloud instances like AWS Lightsail.

## 🚀 Features

- ✅ Multi-tenant (per-user data isolation)
- 📇 CSV + manual prospect import
- 🧾 Email template management (HTML or plain text)
- 🔁 Sequence builder (weekly/monthly intervals)
- ⏱ Smart delivery: weekdays only, random hours (09:00–19:00)
- 📉 Throttling: max emails/hour per user
- 🔁 Automatic retry queue for failed sends
- 🔐 Optional per-user SMTP credentials
- 📊 Logging of email delivery attempts

## 🧱 Project Structure

email_saas/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLModel data models
│   ├── crud.py              # DB access logic (CRUD)
│   ├── scheduler.py         # Scheduling logic & delivery rules
│   ├── auth.py              # Dummy auth or JWT system
│   └── config.py            # Environment variables loader
│
├── worker/
│   ├── __init__.py
│   └── worker.py            # Background email processing worker
│
├── .env                     # Environment settings (SMTP, DB)
├── requirements.txt         # Python package list
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Orchestration for API + Redis
└── README.md                # This documentation

## 🛠 Installation

### Option 1: Local Setup (no Docker)

1. Clone the repo:
   git clone https://github.com/YOUR_USERNAME/email-saas.git
   cd email-saas

2. Set up environment:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Add your environment variables:
   cp .env.example .env
   nano .env

4. Run the API:
   uvicorn app.main:app --reload

### Option 2: Run with Docker

1. Build and run with Docker Compose:
   docker-compose up --build

## ⚙️ Environment Configuration (.env)

DATABASE_URL=sqlite:///./email_saas.db  
SMTP_HOST=smtp.example.com  
SMTP_PORT=587  
SMTP_USER=you@example.com  
SMTP_PASSWORD=your_password  

## 📤 Sending Emails

Send due emails (used by background worker or cron):

curl -X POST http://localhost:8000/send_due_emails/

Or implement an actual background process in `worker/worker.py`.

## 💡 Development Tips

- Modularize logic: keep `models.py`, `crud.py`, `scheduler.py` clean
- Use SQLModel for type-safe ORM
- Use `.env` to isolate secrets and configs
- Plan for email bounce/error handling in future
- Add Stripe/Paddle for monetization later

## 📜 License

MIT — use, modify, or extend freely.

## 🙋 Want Help?

Open an issue or ping me on GitHub! Contributions welcome.

