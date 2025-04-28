import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from odoo import models, fields, api
from datetime import datetime, timedelta

class MailAccount(models.Model):
    _name = 'mail.account'
    _description = 'Mail Account'

    name = fields.Char('Account Name')
    email = fields.Char('Email Address')
    imap_server = fields.Char('IMAP Server')
    imap_port = fields.Integer('IMAP Port')
    smtp_server = fields.Char('SMTP Server')
    smtp_port = fields.Integer('SMTP Port', default=465)
    username = fields.Char('Username')
    password = fields.Char('Password')

    @api.model
    def fetch_mails(self):
        for account in self.search([]):
            try:
                mail = imaplib.IMAP4_SSL(account.imap_server, account.imap_port)
                mail.login(account.username, account.password)
                mail.select('inbox')
                date = (datetime.now() - timedelta(days=60)).strftime("%d-%b-%Y")
                result, data = mail.search(None, f'(SINCE "{date}")')
                ids = data[0].split()
                for num in ids[-10:]:
                    result, data = mail.fetch(num, '(RFC822)')
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    subject = email_message['subject']
                    sender = email_message['from']
                    date_sent = email_message['date']
                    body = ''
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode(errors='ignore')
                    self.env['mail.message'].create({
                        'subject': subject,
                        'body': body,
                        'email_from': sender,
                        'date': date_sent,
                        'model': 'mail.account',
                        'res_id': account.id,
                    })
                mail.logout()
            except Exception as e:
                pass

    def send_mail(self, to, subject, body_html):
        smtp_server = self.smtp_server
        smtp_port = self.smtp_port
        username = self.username
        password = self.password

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = to

        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(username, password)
        server.sendmail(username, [to], msg.as_string())
        server.quit()