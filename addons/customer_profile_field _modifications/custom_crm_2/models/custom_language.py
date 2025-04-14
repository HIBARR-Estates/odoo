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
    
    # Use standard address fields from base module
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)

    child1_age = fields.Integer(string='Child 1 Age')
    child2_age = fields.Integer(string='Child 2 Age')
    # ... etc