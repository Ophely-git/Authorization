# import smtplib
# from email.mime.text import MIMEText
#
# subject = "Email Subject"
# body = "This is the body of the text message"
# sender = 'bigcookingisland@gmail.com'
# recipients = ["bazhenmokhovtsov@gmail.com", "recipient2@gmail.com"]
# password = 'vmqu tdrt wvak rpfe'
#
#
# def send_email(subject, body, sender, recipients, password):
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = sender
#     msg['To'] = ', '.join(recipients)
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
#        smtp_server.login(sender, password)
#        smtp_server.sendmail(sender, recipients, msg.as_string())
#     print("Message sent!")
#

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings')
from django.core.mail import send_mail
send_mail(
    "Subject here",
    "Here is the message.",
    "bigcookingisland@gmail.com",
    ["bazhenmokhovtsov@gmail.com"],
    fail_silently=False,
)
