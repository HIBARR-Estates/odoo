from odoo import models, fields

class CustomLanguage(models.Model):
    _name = 'custom.language'
    _description = 'Custom Language List'
    
    name = fields.Char('Language', required=True, translate=True)
    code = fields.Char('Code', size=5, required=True)
    active = fields.Boolean('Active', default=True)

    languages = fields.Many2many(
        'res.lang',
        'crm_lead_lang_rel',
        'lead_id',
        'lang_id',
        string='Languages'
    )

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
 