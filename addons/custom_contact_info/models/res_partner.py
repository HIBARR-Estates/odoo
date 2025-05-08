from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    employment_status = fields.Selection([
        ('student', 'Student'),
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('retired', 'Retired'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other')
    ], string="Employment Status", tracking=True)
    employment_status_other = fields.Char(string="Other Employment Status", tracking=True)
    occupation = fields.Char(string="Occupation", tracking=True)
    income = fields.Float(string="Income", digits=(16, 2), tracking=True)
    additional_income = fields.Float(string="Additional Income", digits=(16, 2), tracking=True)
    languages = fields.Many2many(
        'custom.language',
        relation='crm_lead_language_rel',
        column1='lead_id',
        column2='language_id',
        string='Languages',
        help="Select the languages you speak",
        tracking=True
    )
    other_languages = fields.Char(string="Other Languages", tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('partner', 'Partner'),
        ('divorced', 'Divorced')
    ], string="Marital Status", tracking=True)
    
    # partner infomation
    partner_first_name = fields.Char(string="Partner's First Name", tracking=True)
    partner_last_name = fields.Char(string="Partner's Last Name", tracking=True)
    partner_city = fields.Char(string="Partner's City", tracking=True)
    partner_country = fields.Many2one('res.country', string="Partner's Country", tracking=True)
    partner_nationality = fields.Many2one('res.country', string="Partner's Nationality", tracking=True)
    partner_employment_status = fields.Selection([
        ('student', 'Student'),
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('retired', 'Retired'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other')
    ], string="Partner's Employment Status", tracking=True)
    partner_employment_status_other = fields.Char(string="Partner's Other Employment Status", tracking=True)
    partner_occupation = fields.Char(string="Partner's Occupation", tracking=True)
    partner_income = fields.Float(string="Partner's Income", digits=(16, 2), tracking=True)
    partner_additional_income = fields.Float(string="Partner's Additional Income", digits=(16, 2), tracking=True)
    partner_languages = fields.Many2many(
        'custom.language',
        relation='crm_lead_language_rel',
        column1='lead_id',
        column2='language_id',
        string='Partner Languages',
        help="Select the languages your partner speaks",
        tracking=True
    )
    partner_other_languages = fields.Char(string="Partner's Other Languages", tracking=True)
    partner_language_other_visible = fields.Boolean(string="Is Partner Other Language Visible", compute="_onchange_partner_languages", store=True)
    # children information
    children_group = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Do you have children?", tracking=True)
    age = fields.Integer(string="Child 1 Age", tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Child 1 Gender", tracking=True)
    age2 = fields.Integer(string="Child 2 Age", tracking=True)
    gender2 = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Child 2 Gender", tracking=True)
    age3 = fields.Integer(string="Child 3 Age", tracking=True)
    gender3 = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Child 3 Gender", tracking=True)
    age4 = fields.Integer(string="Child 4 Age", tracking=True)
    gender4 = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Child 4 Gender", tracking=True)
    age5 = fields.Integer(string="Child 5 Age", tracking=True)
    gender5 = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Child 5 Gender", tracking=True)
    personal_question1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Are you currently living with your children?", tracking=True)
    language_other_visible = fields.Boolean(string="Is Other Language Visible", compute="_onchange_languages", store=True)
    def update_contact_info(self, value):
        for rec in self:
            rec.contact_info = value
    @api.onchange('languages')
    def _onchange_languages(self):
        if self.languages and any(lang.name == 'Other' for lang in self.languages):
            self.language_other_visible = True
        else:
            self.language_other_visible = False

    @api.onchange('partner_languages')
    def _onchange_partner_languages(self):
        if self.partner_languages and any(lang.name == 'Other' for lang in self.partner_languages):
            self.partner_language_other_visible = True
        else:
            self.partner_language_other_visible = False
