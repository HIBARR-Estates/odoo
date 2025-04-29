from odoo import models, fields

class MailAccount(models.Model):
    _name = 'mail.account'
    _description = 'Mail Account'

    name = fields.Char(string="Name")
    smtp_server = fields.Char(string="SMTP Server")
    smtp_port = fields.Integer(string="SMTP Port")