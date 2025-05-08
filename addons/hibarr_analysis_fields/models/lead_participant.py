from odoo import models, fields

class LeadParticipant(models.Model):
    _name = 'lead.participant'
    _description = 'Lead Participant'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    role = fields.Selection([
        ('caller', 'Caller'),
        ('viewer', 'Viewer'),
        ('agent', 'Agent'),
        ('closer', 'Closer')
    ], string='Role', required=True)
