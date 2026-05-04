import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tinkrbell-secret-key-change-me")

    # Database — single URL (works with Supabase, local Postgres, etc.)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://tinkrbell:tinkrbell_pass@db:5432/tinkrbell_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # UPI Payment
    UPI_ID = os.getenv("UPI_ID", "yourname@okicici")
    UPI_NAME = os.getenv("UPI_NAME", "Celestial Readings")

    # WhatsApp (for payment proof)
    WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "919876543210")

    # Admin Credentials
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-immediately")
