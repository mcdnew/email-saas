from dotenv import load_dotenv
import os

# Load from .env file into environment
load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./email_saas.db")

# Default SMTP settings (can be overridden per user)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
