from odoo import models, fields

class CustomLanguage(models.Model):
    _name = 'custom.language'
    _description = 'Custom Language List'

    name = fields.Char('Language', required=True, translate=True)
    code = fields.Char('Code', size=5, required=True)
    active = fields.Boolean('Active', default=True)