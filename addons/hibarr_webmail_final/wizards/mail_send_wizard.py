from odoo import models, fields

class MailSendWizard(models.TransientModel):
    _name = "mail.send.wizard"
    _description = "Send Email Wizard"

    account_id = fields.Many2one("mail.account", required=True)
    to = fields.Char(required=True)
    subject = fields.Char(required=True)
    body_html = fields.Html(required=True)

    def send_email(self):
        self.account_id.send_mail(self.to, self.subject, self.body_html)