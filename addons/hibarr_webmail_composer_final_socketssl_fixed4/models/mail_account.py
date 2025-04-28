import smtplib
import ssl
import socket

from odoo import models, fields, api
from odoo.exceptions import UserError

class MailAccount(models.Model):
    _name = 'mail.account'
    _description = 'Mail Account'

    name = fields.Char('Account Name', required=True)
    smtp_server = fields.Char('SMTP Server', required=True)
    smtp_port = fields.Integer('SMTP Port', required=True)
    smtp_user = fields.Char('SMTP Username', required=True)
    smtp_password = fields.Char('SMTP Password', required=True)

    @api.model
    def send_mail(self, to_email, subject, body_html):
        smtp_server = self.smtp_server
        smtp_port = self.smtp_port
        username = self.smtp_user
        password = self.smtp_password

        context = ssl.create_default_context()
        with socket.create_connection((smtp_server, smtp_port)) as sock:
            with ssl.wrap_socket(sock) as ssl_sock:
                server = smtplib.SMTP_SSL()
                server.sock = ssl_sock
                server.file = server.sock.makefile('rb')
                server.helo()
                server.login(username, password)

                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart

                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = username
                msg['To'] = to_email

                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)

                server.sendmail(username, to_email, msg.as_string())
                server.quit()

    def smtp_test_connection(self):
        self.ensure_one()
        try:
            self.send_mail(self.smtp_user, 'Test E-Mail', '<b>Dies ist eine Test-E-Mail vom HIBARR CRM</b>')
        except Exception as e:
            raise UserError(f"Verbindung fehlgeschlagen: {e}")
