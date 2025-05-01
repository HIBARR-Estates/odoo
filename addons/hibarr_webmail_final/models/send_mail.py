from odoo import models, fields, api
import smtplib, ssl
import imaplib

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
    def create(self, vals):
        if not vals.get('body'):
            signature = self.env.user.signature or ''
            vals['body'] = f'<br><br>{signature}' if signature else ''
        return super().create(vals)

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
        return {'type': 'ir.actions.act_window_close'}

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
                to_addresses = [email.strip() for email in self.recipient_email.split(',') if email.strip()]
                message = f"From: {sender}\nTo: {', '.join(to_addresses)}\nSubject: {self.subject}\n\n{self.body}"
                server.sendmail(account.smtp_user, to_addresses, message)
            self.state = 'sent'
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

