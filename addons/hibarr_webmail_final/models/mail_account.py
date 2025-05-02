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
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)

    def test_smtp_connection(self):
        for account in self:
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(account.smtp_server, account.smtp_port, context=context) as server:
                    server.login(account.smtp_user, account.smtp_password)
                return True
            except Exception as e:

                return str(e)

    def action_test_smtp(self):
        self.ensure_one()
        result = self.test_smtp_connection()
        if result is True:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'SMTP Test Successful',
                    'message': 'The SMTP connection was successful.',
                    'type': 'success',
                    'sticky': False,
                },
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'SMTP Test Failed',
                    'message': f'Error: {result}',
                    'type': 'danger',
                    'sticky': True,
                },
            }