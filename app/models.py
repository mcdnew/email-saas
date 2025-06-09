from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProspectType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    description: Optional[str] = None
    default_language: Optional[str] = "en"
    default_sequence_id: Optional[int] = Field(default=None, foreign_key="sequence.id")

    max_emails_per_hour: Optional[int] = 10
    send_window_start: Optional[int] = 9
    send_window_end: Optional[int] = 18
    delay_strategy: Optional[str] = "default"


class Prospect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    email: str
    language: str
    type_id: int = Field(foreign_key="prospecttype.id")
    sequence_id: Optional[int] = Field(default=None, foreign_key="sequence.id")
    status: str = "pending"
    last_contacted: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Template(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    language: str
    prospect_type: str
    subject: str
    body: str
    is_html: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Sequence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SequenceStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sequence_id: int = Field(foreign_key="sequence.id")
    template_id: int = Field(foreign_key="template.id")
    step_number: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduledEmail(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    prospect_id: int = Field(foreign_key="prospect.id")
    template_id: int = Field(foreign_key="template.id")
    scheduled_for: datetime
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    status: str = "pending"
    sent_at: Optional[datetime] = None
