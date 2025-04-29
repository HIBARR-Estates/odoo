
from odoo import models, fields

class MailAccount(models.Model):
    _name = 'mail.account'
    _description = 'Mail Account'

    name = fields.Char(required=True)
    smtp_server = fields.Char(string="SMTP Server", required=True)
    smtp_port = fields.Integer(string="SMTP Port", required=True)
