from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Analysis Fields
    analysis_status = fields.Selection([
        ('pending', 'Pending Analysis'),
        ('in_progress', 'Analysis in Progress'),
        ('completed', 'Analysis Completed'),
        ('on_hold', 'Analysis On Hold'),
    ], string='Analysis Status', default='pending')

    analysis_notes = fields.Text(string='Analysis Notes')
    analysis_date = fields.Date(string='Analysis Date')
    analysis_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Analysis Priority', default='medium')

    # Analysis Metrics
    analysis_score = fields.Float(string='Analysis Score', digits=(3, 2))
    analysis_completion = fields.Float(string='Analysis Completion %', digits=(3, 2))
    analysis_risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], string='Risk Level')

    # Analysis Tags
    analysis_tags = fields.Many2many(
        'analysis.tag',
        'crm_lead_analysis_tag_rel',
        'lead_id',
        'tag_id',
        string='Analysis Tags'
    ) 