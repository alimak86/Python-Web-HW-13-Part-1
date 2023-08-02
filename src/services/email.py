from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

# CONFIGURATION = ConnectionConfig(
#     MAIL_USERNAME="put_nik4@mail.ru",
#     MAIL_PASSWORD="uHJNrYCdcLHHshn5zs6G",
#     MAIL_FROM=EmailStr("put_nik4@mail.ru"),
#     MAIL_PORT=465,
#     MAIL_SERVER="smtp.mail.ru",
#     MAIL_FROM_NAME="Alisa",
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
#     TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
# )

CONFIGURATION = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Alisa",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

class Email_Service:
    def __init__(self, conf):
        self.conf = conf

    async def send_email(self, email: EmailStr, username: str, host: str):
        try:
            token_verification = auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email ",
                recipients=[email],
                template_body={"host": host, "username": username, "token": token_verification},
                subtype=MessageType.html
            )

            fm = FastMail(self.conf)
            await fm.send_message(message, template_name="email_template.html")
        except ConnectionErrors as err:
            print(err)

email_service = Email_Service(CONFIGURATION)