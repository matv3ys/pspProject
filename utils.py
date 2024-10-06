import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from config import settings

def send_code_email(code: int, recipient: str):
    from_email, password = settings.GET_EMAIL_AND_PASSWORD

    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as server:
        msg = MIMEText(f"Ваш код подтверждения: {code}")
        msg['Subject'] = "Регистрация в TestingSystem"
        msg['From'] = formataddr(('TestingSystem', from_email))
        msg['To'] = recipient
        server.login(from_email, password)
        server.sendmail(from_email, recipient, msg.as_string())
