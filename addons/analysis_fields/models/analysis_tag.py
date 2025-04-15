from odoo import models, fields

class AnalysisTag(models.Model):
    _name = 'analysis.tag'
    _description = 'Analysis Tag'

    name = fields.Char(string='Tag Name', required=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True) 