import smtplib, os
from core.enums import OperationType
from email.message import EmailMessage

def send_email(to, condition, email, password):
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

