from odoo import models, fields, api
import smtplib, ssl
import imaplib

class SendMail(models.Model):
    _name = 'send.mail'
    _description = 'Send Mail'

    recipient_email = fields.Char(string='Recipient Email', required=True)
    subject = fields.Char(string='Subject', required=True)
    body = fields.Text(string='Body', required=True)
    mail_account_id = fields.Many2one('mail.account', string='Mail Account', required=True)

    def action_send_mail(self):
        self.ensure_one()
        if not self.mail_account_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Please select a mail account.',
                    'type': 'danger',
                    'sticky': True,
                }
            }
        account = self.mail_account_id
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(account.smtp_server, account.smtp_port, context=context) as server:
                server.login(account.smtp_user, account.smtp_password)
                sender = f"{account.name} <{account.smtp_user}>" if account.name else account.smtp_user
                message = f"""From: {sender}\nTo: {self.recipient_email}\nSubject: {self.subject}\n\n{self.body}"""
                server.sendmail(account.smtp_user, self.recipient_email, message)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Email sent successfully',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Failed to send email: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

