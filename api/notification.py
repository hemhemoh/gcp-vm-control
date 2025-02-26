import smtplib, os
from core.enums import OperationType
from email.message import EmailMessage

email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")

def send_email(to, condition):
    msg = EmailMessage()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email, password)
    if condition == OperationType.START:
        msg.set_content("Server has been started")
    elif condition == OperationType.STOP:
        msg.set_content("Server has been stopped")
    msg['Subject'] = str(condition)
    msg['From'] = "mardiyyahtesting@gmail.com"
    msg['To'] = to
    server.send_message(msg)
    server.quit()
