     
import smtplib
from email.message import EmailMessage

EMAIL_USER = "asthasingh00442@gmail.com"
EMAIL_PASS = "yzjs otzo nlvh pcae"  # Use Gmail App Password

def send_email_alert(df, attachment_path, recipient_email):
    msg = EmailMessage()
    msg['Subject'] = '🚨 Fund Misuse Alert'
    msg['From'] = EMAIL_USER
    msg['To'] = recipient_email
    msg.set_content('Suspicious fund usage has been detected. Please see the attached report.')

    with open(attachment_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=attachment_path)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
