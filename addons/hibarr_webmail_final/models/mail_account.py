from odoo import models, fields
import smtplib, ssl

class MailAccount(models.Model):
    _name = "mail.account"
    _description = "Mail Account"

    name = fields.Char(required=True)
    smtp_server = fields.Char(required=True)
    smtp_port = fields.Integer(required=True, default=465)
    smtp_user = fields.Char(required=True)
    smtp_password = fields.Char(required=True)

    def send_mail(self, to_address, subject, body_html):
        for account in self:
            message = f"""From: {account.smtp_user}\r\nTo: {to_address}\r\nSubject: {subject}\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{body_html}"""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(account.smtp_server, account.smtp_port, context=context) as server:
                server.login(account.smtp_user, account.smtp_password)
                server.sendmail(account.smtp_user, to_address, message.encode('utf-8'))