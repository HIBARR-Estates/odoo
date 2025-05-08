from odoo import models, fields

class CheckboxAddons(models.Model):
    _name = 'checkboxes.addons'
    _description = 'Checkbox Addons'
    _order = 'name'

    name = fields.Char(string='Addon Name', required=True, translate=True)
    addon_type = fields.Selection([
        ('amenity', 'Amenity'),
        ('interior', 'Interior'),
        ('infrastructure', 'Infrastructure'),
        ('assets', 'Assets for Sale'),
        ('permit_needs', 'Permit Needs'),
        ('education_needs', 'Education Needs'),
        ('insurance_needs', 'Insurance Needs'),
        ('legal_needs', 'Legal Needs'),
        ('car_needs', 'Car Needs'),
        ('investment_needs', 'Investment Needs'),
        ('banking_needs', 'Banking Needs'),
        ('cooperation', 'Cooperation')
    ], string='Checkbox Type', required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')