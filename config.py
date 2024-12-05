import os
from dotenv import load_dotenv

load_dotenv()

WORK_API_URL = os.getenv("WORK_API_URL")
WORK_API_USERNAME = os.getenv("WORK_API_USERNAME")
WORK_API_PASSWORD = os.getenv("WORK_API_PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")

CRM_API_URL = os.getenv("CRM_API_URL")
CRM_API_KEY = os.getenv("CRM_API_KEY")

REDIS_URL = os.getenv("REDIS_URL")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

PIPELINE_ID = os.getenv("PIPELINE_ID")
SOURCE_ID = os.getenv("SOURCE_ID")

SMTP_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": int(os.getenv("SMTP_PORT")),
    "smtp_username": os.getenv("SMTP_USERNAME"),
    "smtp_password": os.getenv("SMTP_PASSWORD"),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "admin_email": os.getenv("ADMIN_EMAIL"),
}
