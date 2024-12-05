import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationClient:
    def __init__(
        self,
        smtp_server,
        smtp_port,
        smtp_username,
        smtp_password,
        sender_email,
        admin_email,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email
        self.admin_email = admin_email

    def create_email(self, subject, cards):
        body = "<h1>CRM Activity Report: Card Creation and Updates</h1><ul>"
        for card in cards:
            card_url = f"https://mgdevelopment.keycrm.app/app/leads/{card['id']}"
            body += f"<li>Card <a href='{card_url}'>#{card['id']}</a> was {card['action']}.</li>"
        body += "</ul>"

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.admin_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        return msg

    def send_email(self, msg):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Email sending error: {e}")

    def send_summary_notification(self, cards):
        if not cards:
            return

        subject = "CRM Activity Report"
        msg = self.create_email(subject, cards)
        self.send_email(msg)
