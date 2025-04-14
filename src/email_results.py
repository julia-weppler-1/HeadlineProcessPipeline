import os
import smtplib
from email.message import EmailMessage

def send_email_with_attachment(subject, body, attachment_path,
                               sender_email, receiver_email,
                               smtp_server, smtp_port, smtp_username, smtp_password):
    # Create the email message object
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(body)

    # Read the attachment file and add it to the email
    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
    # Set the MIME type for Excel files (for .xlsx)
    msg.add_attachment(file_data, maintype="application",
                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       filename=file_name)

    # Connect to the SMTP server using SSL and send the message
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
