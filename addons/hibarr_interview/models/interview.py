from odoo import models, fields, api



class CrmLead(models.Model):
    _inherit = 'crm.lead'

    kick_off_meeting = fields.Date(string='Kick Off meeting Date')
    kick_off_meeting_time = fields.Float(string='Kick Off meeting Time')
    kick_off_meeting_follow_up = fields.Text(string='Kick Off meeting Follow Up')

