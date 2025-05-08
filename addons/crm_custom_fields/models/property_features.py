from odoo import models, fields

class PropertyFeature(models.Model):
    _name = 'property.feature'
    _description = 'Property Features'
    _order = 'name'

    name = fields.Char(string='Feature Name', required=True, translate=True)
    feature_type = fields.Selection([
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
    ], string='Feature Type', required=True)
    _ondelete_methods = ['cascade']
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description') 