import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

# Load variables from .env into the system environment
load_dotenv()
conf = ConnectionConfig(
    MAIL_USERNAME="het.modi@armakuni.com",
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    
    
    
    MAIL_FROM="het.modi@armakuni.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)