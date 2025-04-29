
from odoo import models, fields, api

class MailSendWizard(models.TransientModel):
    _name = 'mail.send.wizard'
    _description = 'Send Email Wizard'

    to = fields.Char(string="To", required=True)
    subject = fields.Char(string="Subject", required=True)
    body_html = fields.Text(string="Body", required=True)

    def send_email(self):
        account = self.env['mail.account'].search([], limit=1)
        account.send_mail(self.to, self.subject, self.body_html)
