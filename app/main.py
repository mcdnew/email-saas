"""
main.py

This is the main FastAPI entry point for the Email SaaS Scheduler.

It will:
- Set up the app and middleware
- Define routes for creating and listing:
    - Prospect Types
    - Prospects
    - Templates
    - Sequences
    - Sequence Steps
    - Trigger the scheduler to send due emails
- Use all supporting modules:
    - models.py (data definitions)
    - crud.py (DB logic)
    - scheduler.py (scheduling logic)
    - auth.py (dummy login context)
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from datetime import datetime

from app import models, crud, scheduler, auth
from app.config import DATABASE_URL

# ----------------- FastAPI + DB Setup -----------------
engine = create_engine(DATABASE_URL, echo=False)
app = FastAPI()

# Enable CORS to allow browser-based clients (optional for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables at startup if they don’t exist
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Dependency: database session (used in all routes)
def get_session():
    with Session(engine) as session:
        yield session

# ----------------- Prospect Types -----------------
@app.post("/prospect-types/")
def create_prospect_type(data: models.ProspectType, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    data.user_id = user.id
    return crud.create_prospect_type(session, data)

@app.get("/prospect-types/")
def list_prospect_types(session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    return crud.get_prospect_types(session, user.id)

# ----------------- Prospects -----------------
@app.post("/prospects/")
def create_prospect(data: models.Prospect, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    data.user_id = user.id
    prospect = crud.create_prospect(session, data)

    # Automatically schedule emails when a prospect is created
    scheduler.schedule_sequence_for_prospect(session, prospect, user.id)
    return prospect

@app.get("/prospects/")
def list_prospects(session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    return crud.get_prospects(session, user.id)

# ----------------- Templates -----------------
@app.post("/templates/")
def create_template(data: models.Template, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    data.user_id = user.id
    return crud.create_template(session, data)

@app.get("/templates/")
def list_templates(session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    return crud.get_templates(session, user.id)

# ----------------- Sequences -----------------
@app.post("/sequences/")
def create_sequence(data: models.Sequence, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    data.user_id = user.id
    return crud.create_sequence(session, data)

@app.get("/sequences/")
def list_sequences(session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    return crud.get_sequences(session, user.id)

# ----------------- Sequence Steps -----------------
@app.post("/sequence-steps/")
def create_sequence_step(data: models.SequenceStep, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    return crud.create_sequence_step(session, data)

@app.get("/sequence-steps/{sequence_id}")
def list_sequence_steps(sequence_id: int, session: Session = Depends(get_session)):
    return crud.get_sequence_steps(session, sequence_id)

# ----------------- Trigger Email Sending -----------------
@app.post("/send-due-emails/")
def send_due_emails(session: Session = Depends(get_session)):
    from app.models import ScheduledEmail
    from app.crud import get_due_emails

    now = datetime.now()
    due_emails = get_due_emails(session, now)

    # Simulate sending logic (replace with real SMTP call later)
    for email in due_emails:
        print(f"Simulating send to prospect {email.prospect_id} (template {email.template_id}) at {now}")
        email.status = "sent"
        email.sent_at = now
        session.add(email)

    session.commit()
    return {"sent": len(due_emails)}
