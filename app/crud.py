from sqlmodel import Session, select
from app.models import (
    User, Prospect, Template, Sequence, SequenceStep,
    ScheduledEmail, ProspectType
)


# ---------- PROSPECT TYPE ----------

def create_prospect_type(session: Session, data: ProspectType) -> ProspectType:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def get_prospect_types(session: Session, user_id: int):
    return session.exec(select(ProspectType).where(ProspectType.user_id == user_id)).all()


# ---------- PROSPECT ----------

def create_prospect(session: Session, data: Prospect) -> Prospect:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def get_prospects(session: Session, user_id: int):
    return session.exec(select(Prospect).where(Prospect.user_id == user_id)).all()


# ---------- TEMPLATE ----------

def create_template(session: Session, data: Template) -> Template:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def get_templates(session: Session, user_id: int):
    return session.exec(select(Template).where(Template.user_id == user_id)).all()


# ---------- SEQUENCE ----------

def create_sequence(session: Session, data: Sequence) -> Sequence:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def get_sequences(session: Session, user_id: int):
    return session.exec(select(Sequence).where(Sequence.user_id == user_id)).all()


# ---------- SEQUENCE STEP ----------

def create_sequence_step(session: Session, data: SequenceStep) -> SequenceStep:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def get_sequence_steps(session: Session, sequence_id: int):
    return session.exec(select(SequenceStep).where(SequenceStep.sequence_id == sequence_id)).all()


# ---------- SCHEDULED EMAIL ----------

def schedule_email(session: Session, email: ScheduledEmail) -> ScheduledEmail:
    session.add(email)
    session.commit()
    session.refresh(email)
    return email

def get_due_emails(session: Session, now):
    return session.exec(
        select(ScheduledEmail).where(
            ScheduledEmail.scheduled_for <= now,
            ScheduledEmail.status == "pending"
        )
    ).all()
