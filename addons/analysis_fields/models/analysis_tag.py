from odoo import models, fields

class AnalysisTag(models.Model):
    _name = 'analysis.tag'
    _description = 'Analysis Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color Index', default=1)
    active = fields.Boolean(default=True) 