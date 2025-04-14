from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # # Address fields to be added before tabs
    # street = fields.Char(string='Street')
    # street2 = fields.Char(string='Street2')
    # zip = fields.Char(string='Zip')
    # city = fields.Char(string='City')
    # country_id = fields.Many2one('res.country', string='Country')
   
       # Use standard address fields from base module
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)
    nationality = fields.Many2one('res.country', string='Nationality')

    # Personal Information Tab
    age_range = fields.Selection([
        ('under_20', 'Under 20'),
        ('20_25', '20-25'),
        ('26_30', '26-30'),
        ('31_40', '31-40'),
        ('41_50', '41-50'),
        ('51_65', '51-65'),
        ('65_plus', '65+'),
    ], string='Age Range')

    employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
    ], string='Employment Status')

    occupation = fields.Char(string='Occupation')
    income = fields.Char(string='Income')
    
    languages = fields.Many2many(
        'res.lang',
        'crm_lead_lang_rel',
        'lead_id',
        'lang_id',
        string='Languages'
    )
    
    other_languages = fields.Char(string='Other Languages')
    
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('partner', 'Partner'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string='Marital Status')

    # Partner Information
    partner_firstname = fields.Char(string='Partner Firstname')
    partner_surname = fields.Char(string='Partner Surname')
    partner_nationality = fields.Many2one('res.country', string='Partner Nationality')
    partner_country = fields.Many2one('res.country', string='Partner Country')
    partner_city = fields.Char(string='Partner City')
    partner_age_range = fields.Selection([
        ('under_20', 'Under 20'),
        ('20_25', '20-25'),
        ('26_30', '26-30'),
        ('31_40', '31-40'),
        ('41_50', '41-50'),
        ('51_65', '51-65'),
        ('65_plus', '65+'),
    ], string='Partner Age Range')

    partner_employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
    ], string='Partner Employment Status')

    partner_occupation = fields.Char(string='Partner Occupation')
    partner_income = fields.Char(string='Partner Income')
    
    partner_languages = fields.Many2many(
        'res.lang',
        'crm_lead_partner_lang_rel',
        'lead_id',
        'lang_id',
        string='Partner Languages'
    )
    
    partner_other_languages = fields.Char(string='Partner Other Languages')
    
    # Children Information (updated age fields)
    living_with_children = fields.Boolean(string='Living with Children?')
    
    child1_age = fields.Char(string='Child 1 Age')
    child1_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 1 Gender')
    
    child2_age = fields.Char(string='Child 2 Age')
    child2_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 2 Gender')
    
    child3_age = fields.Char(string='Child 3 Age')
    child3_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 3 Gender')
    
    child4_age = fields.Char(string='Child 4 Age')
    child4_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 4 Gender')
    
    child5_age = fields.Char(string='Child 5 Age')
    child5_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 5 Gender')
    
    #language options    
    # lang_De = fields.Boolean('German')
    # lang_En = fields.Boolean('English')
    # lang_Ar = fields.Boolean('Arabic')
    # lang_Tr = fields.Boolean('Turkish')
    # lang_Ru = fields.Boolean('Russian')
    # language_select = fields.Char(string='Languages')

    languages = fields.Many2many(
        'custom.language',
        string='Languages',
        relation='crm_lead_lang_rel',
        column1='lead_id',
        column2='lang_id'
    )

    partner_languages = fields.Many2many(
        'custom.language',
        string='Partner Languages',
        relation='crm_lead_partner_lang_rel',
        column1='lead_id',
        column2='lang_id'
    )
