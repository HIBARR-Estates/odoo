from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Personal Information
    age_range = fields.Selection([
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46-55', '46-55'),
        ('56-65', '56-65'),
        ('65+', '65+'),
    ], string='Age Range')

    employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ], string='Employment Status')

    occupation = fields.Char(string='Occupation')
    income = fields.Float(string='Income')
    languages = fields.Many2many('analysis.language', string='Languages')
    other_languages = fields.Char(string='Other Languages')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string='Marital Status')

    # Partner Information
    partner_firstname = fields.Char(string='Partner First Name')
    partner_surname = fields.Char(string='Partner Surname')
    partner_nationality = fields.Char(string='Partner Nationality')
    partner_country = fields.Many2one('res.country', string='Partner Country')
    partner_city = fields.Char(string='Partner City')
    partner_age_range = fields.Selection([
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46-55', '46-55'),
        ('56-65', '56-65'),
        ('65+', '65+'),
    ], string='Partner Age Range')

    partner_employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ], string='Partner Employment Status')

    partner_occupation = fields.Char(string='Partner Occupation')
    partner_income = fields.Float(string='Partner Income')
    partner_languages = fields.Many2many('analysis.language', string='Partner Languages')
    partner_other_languages = fields.Char(string='Partner Other Languages')

    # Children Information
    child1_age = fields.Integer(string='Child 1 Age')
    child1_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 1 Gender')

    child2_age = fields.Integer(string='Child 2 Age')
    child2_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 2 Gender')

    child3_age = fields.Integer(string='Child 3 Age')
    child3_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 3 Gender')

    child4_age = fields.Integer(string='Child 4 Age')
    child4_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 4 Gender')

    child5_age = fields.Integer(string='Child 5 Age')
    child5_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Child 5 Gender')

    living_with_children = fields.Boolean(string='Living with Children')

 