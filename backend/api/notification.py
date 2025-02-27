import smtplib
from core.enums import OperationType
from email.message import EmailMessage

def send_email(sender, receiver, condition, password):
    msg = EmailMessage()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    if condition == OperationType.START:
        msg.set_content("Server has been started")
    elif condition == OperationType.STOP:
        msg.set_content("Server has been stopped")
    msg['Subject'] = str(condition)
    msg['From'] = sender
    msg['To'] = receiver
    server.send_message(msg)
    server.quit()

