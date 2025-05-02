from odoo import models, fields, api
import smtplib, ssl
import imaplib
from email.mime.text import MIMEText

class SendMail(models.Model):
    _name = 'send.mail'
    _description = 'Send Mail'

    recipient_email = fields.Char(string='Recipient Email', required=True)
    subject = fields.Char(string='Subject', required=True)
    body = fields.Text(string='Body', required=True, default=lambda self: self._default_body())
    mail_account_id = fields.Many2one('mail.account', string='Mail Account', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled')
    ], default='draft', string='Status')

    @api.model
    def _default_body(self):
        signature = self.env.user.signature or ''
        return f'<br><br>{signature}' if signature else ''

    @api.model
    def create(self, vals_list):
        # Support both single and batch create
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        for vals in vals_list:
            if not vals.get('body'):
                signature = self.env.user.signature or ''
                vals['body'] = f'<br><br>{signature}' if signature else ''
        return super().create(vals_list)

    def action_save_draft(self):
        self.ensure_one()
        self.state = 'draft'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Draft saved.',
                'type': 'info',
                'sticky': False,
            }
        }

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        res = {'type': 'ir.actions.act_window_close'}
        self.unlink()  # Delete the record after cancelling
        return res

    def action_send_mail(self):
        self.ensure_one()
        if not self.mail_account_id or self.mail_account_id.user_id != self.env.user:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'You are not allowed to use this mail account.',
                    'type': 'danger',
                    'sticky': True,
                }
            }
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
                to_addresses = [email.strip() for email in self.recipient_email.split(',') if email.strip()]
                msg = MIMEText(self.body, "html")
                msg["From"] = sender
                msg["To"] = ", ".join(to_addresses)
                msg["Subject"] = self.subject
                server.sendmail(account.smtp_user, to_addresses, msg.as_string())
            self.state = 'sent'
            res = {'type': 'ir.actions.act_window_close'}
            self.unlink()  # Delete the record after sending
            return res
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

