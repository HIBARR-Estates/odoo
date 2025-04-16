from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Analysis Fields
    partner_analysis_status = fields.Selection([
        ('pending', 'Pending Analysis'),
        ('in_progress', 'Analysis in Progress'),
        ('completed', 'Analysis Completed'),
        ('on_hold', 'Analysis On Hold'),
    ], string='Analysis Status', default='pending')

    partner_analysis_notes = fields.Text(string='Analysis Notes')
    partner_analysis_date = fields.Date(string='Analysis Date')
    partner_analysis_score = fields.Float(string='Analysis Score', digits=(5, 2))
    
    # Analysis Tags
    partner_analysis_tags = fields.Many2many(
        'analysis.tag',
        'partner_analysis_tag_rel',
        'partner_id',
        'tag_id',
        string='Analysis Tags'
    ) 