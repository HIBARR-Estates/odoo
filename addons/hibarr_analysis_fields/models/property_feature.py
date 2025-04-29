from odoo import models, fields

class PropertyFeature(models.Model):
    _name = 'property.feature'
    _description = 'Property Features'

    name = fields.Char(string='Name', required=True)
    feature_type = fields.Selection([
        ('amenity', 'Amenity'),
        ('interior', 'Interior'),
        ('infrastructure', 'Infrastructure'),
        ('assets', 'Assets'),
        ('permit_needs', 'Permit Needs'),
        ('education_needs', 'Education Needs'),
        ('insurance_needs', 'Insurance Needs'),
        ('legal_needs', 'Legal Needs'),
        ('car_needs', 'Car Needs'),
        ('investment_needs', 'Investment Needs'),
        ('banking_needs', 'Banking Needs'),
        ('cooperation', 'Cooperation')
    ], string='Feature Type', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
