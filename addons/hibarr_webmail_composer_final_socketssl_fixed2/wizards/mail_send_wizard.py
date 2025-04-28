from odoo import models, fields

class MailSendWizard(models.TransientModel):
    _name = 'mail.send.wizard'
    _description = 'Send Mail Wizard'

    to = fields.Char('To', required=True)
    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)

    def send_email(self):
        account = self.env['mail.account'].search([], limit=1)
        account.send_mail(self.to, self.subject, self.body_html)