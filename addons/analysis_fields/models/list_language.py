from odoo import models, fields, api

class Language(models.Model):
    _name = 'analysis.language'
    _description = 'Language'
    _order = 'name'

    name = fields.Char(string='Language', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(default=True) 