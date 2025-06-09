from fastapi import Depends, HTTPException, status
from app.models import User

# Dummy user to simulate login
# Later, replace with JWT or session-based system
def get_current_user() -> User:
    return User(
        id=1,
        email="admin@example.com",
        hashed_password="dummy",
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="admin@example.com",
        smtp_password="your_password"
    )
