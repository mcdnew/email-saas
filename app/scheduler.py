# What This Does:
# Pulls the delay strategy and working hours from ProspectType
# Applies:
#   - Weekly spacing for the first 4 steps
#   - Monthly spacing after that
#   - Randomly schedules each email in the 09:00–19:00 window
#   - Skips weekends
#   - Persists to the database

from datetime import datetime, timedelta, time, date
import random
from sqlmodel import Session, select

from app.models import ScheduledEmail, Prospect, SequenceStep, ProspectType
from app.crud import schedule_email

def get_next_weekday(start_date: date) -> date:
    while start_date.weekday() > 4:  # Skip Saturday/Sunday
        start_date += timedelta(days=1)
    return start_date

def generate_send_time_for_day(day: date, start_hour: int, end_hour: int) -> datetime:
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return datetime.combine(day, time(hour, minute))

def schedule_sequence_for_prospect(session: Session, prospect: Prospect, user_id: int):
    # Load the prospect type settings
    type_config = session.exec(
        select(ProspectType).where(ProspectType.id == prospect.type_id)
    ).first()

    # Load sequence steps
    steps = session.exec(
        select(SequenceStep).where(SequenceStep.sequence_id == prospect.sequence_id)
    ).all()

    start_date = date.today()
    delay_strategy = type_config.delay_strategy if type_config else "default"
    start_hour = type_config.send_window_start if type_config else 9
    end_hour = type_config.send_window_end if type_config else 19

    for step in steps:
        # Compute offset
        if delay_strategy == "aggressive":
            offset_days = 2 * step.step_number
        elif delay_strategy == "slow":
            offset_days = 14 * step.step_number
        else:  # default
            if step.step_number <= 4:
                offset_days = 7 * step.step_number
            else:
                offset_days = (7 * 4) + (30 * (step.step_number - 4))

        target_date = get_next_weekday(start_date + timedelta(days=offset_days))
        scheduled_for = generate_send_time_for_day(target_date, start_hour, end_hour)

        scheduled = ScheduledEmail(
            user_id=user_id,
            prospect_id=prospect.id,
            template_id=step.template_id,
            scheduled_for=scheduled_for
        )

        schedule_email(session, scheduled)
