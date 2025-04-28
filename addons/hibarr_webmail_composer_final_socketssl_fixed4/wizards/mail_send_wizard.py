from odoo import models, fields
from odoo.exceptions import UserError

class MailSendWizard(models.TransientModel):
    _name = 'mail.send.wizard'
    _description = 'Send Email Wizard'

    to = fields.Char('To', required=True)
    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)

    def send_email(self):
        self.ensure_one()
        account = self.env['mail.account'].search([], limit=1)
        if not account:
            raise UserError('Keine Mail-Account konfiguriert!')
        account.send_mail(self.to, self.subject, self.body_html)
