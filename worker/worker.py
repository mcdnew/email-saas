"""
worker.py

This background script processes scheduled emails:

- Loads scheduled emails that are due to be sent
- Uses each user's SMTP settings (or fallback to global SMTP)
- Renders the email using Jinja2 with placeholders like {{name}}, {{email}}, etc.
- Sends real emails via SMTP (HTML or plain text)
- Handles retries with backoff if sending fails
"""

from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
import smtplib
from email.mime.text import MIMEText
from jinja2 import Template as JinjaTemplate

from app.models import ScheduledEmail, User, Template, Prospect
from app.config import DATABASE_URL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# Connect to your FastAPI database
engine = create_engine(DATABASE_URL, echo=False)

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY_MINUTES = 15

# Renders {{placeholders}} in the email body using Prospect fields
def render_email(template_str: str, context: dict) -> str:
    try:
        jinja_template = JinjaTemplate(template_str)
        return jinja_template.render(**context)
    except Exception as e:
        print(f"[!] Error rendering template: {e}")
        return template_str  # fallback

# Sends a real email via SMTP
def send_email_via_smtp(sender_email, sender_pass, smtp_host, smtp_port, to_email, subject, body, is_html=False):
    msg = MIMEText(body, "html" if is_html else "plain")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)

# Main email processing logic
def process_due_emails():
    now = datetime.now()
    with Session(engine) as session:
        due_emails = session.exec(
            select(ScheduledEmail).where(
                ScheduledEmail.scheduled_for <= now,
                ScheduledEmail.status == "pending"
            )
        ).all()

        print(f"[{now}] Processing {len(due_emails)} due emails...")

        for email in due_emails:
            user = session.get(User, email.user_id)
            template = session.get(Template, email.template_id)
            prospect = session.get(Prospect, email.prospect_id)

            # Prepare template context from Prospect fields
            context = {
                "name": prospect.name,
                "email": prospect.email,
                "language": prospect.language,
                "type": prospect.type_id,
            }

            # Render body using placeholders
            rendered_body = render_email(template.body, context)

            # Choose SMTP settings (user or fallback)
            smtp_user = user.smtp_user or SMTP_USER
            smtp_pass = user.smtp_password or SMTP_PASSWORD
            smtp_host = user.smtp_host or SMTP_HOST
            smtp_port = user.smtp_port or SMTP_PORT

            try:
                # Send the email
                send_email_via_smtp(
                    sender_email=smtp_user,
                    sender_pass=smtp_pass,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    to_email=prospect.email,
                    subject=template.subject,
                    body=rendered_body,
                    is_html=template.is_html
                )

                # Mark success
                email.status = "sent"
                email.sent_at = now
                print(f"[✓] Sent to {prospect.email}")

            except Exception as e:
                # On failure: retry or mark failed
                email.retry_count += 1
                email.last_attempt = now

                if email.retry_count >= MAX_RETRIES:
                    email.status = "failed"
                    print(f"[X] Failed: {prospect.email} after {MAX_RETRIES} tries → {str(e)}")
                else:
                    # Reschedule for later
                    delay = timedelta(minutes=RETRY_DELAY_MINUTES * email.retry_count)
                    email.scheduled_for = now + delay
                    print(f"[!] Retry for {prospect.email} in {delay} → {str(e)}")

            session.add(email)

        session.commit()

# Run the script
if __name__ == "__main__":
    print(f"Worker started at {datetime.now()}")
    process_due_emails()

