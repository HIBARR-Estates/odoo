from odoo import models, fields, api
import smtplib, ssl
import imaplib
import email

class Mailbox(models.Model):
    _name = 'webmail.mailbox'
    _description = 'Mailbox'

    name = fields.Char(string='Mailbox Name', required=True)
    smtp_server = fields.Char(string='SMTP Server', required=True)
    smtp_port = fields.Integer(string='SMTP Port', required=True, default=465)
    smtp_user = fields.Char(string='SMTP User', required=True)
    smtp_password = fields.Char(string='SMTP Password', required=True)
    imap_server = fields.Char(string='IMAP Server', required=True)
    imap_port = fields.Integer(string='IMAP Port', required=True, default=993)

    def send_email(self, to_address, subject, body):
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.smtp_user, self.smtp_password)
                message = f"From: {self.smtp_user}\nTo: {to_address}\nSubject: {subject}\n\n{body}"
                server.sendmail(self.smtp_user, to_address, message)
            return True
        except smtplib.SMTPException as e:
            return f"SMTP error occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def fetch_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_user, self.smtp_password)
            mail.select('inbox')
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            emails = []
            for e_id in email_ids[-10:]:  # Fetch the last 10 emails
                status, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append({
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'body': msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                })
            mail.logout()
            return emails
        except Exception as e:
            return str(e)