{
    'name': 'Custom Contact Information',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Add custom fields to contacts',
    'description': """
        This module adds custom fields to contact form in Odoo 18.
        Features:
        - Additional contact information fields
        - Custom language management
        - Contact language proficiency tracking
        - Field change tracking in chatter
    """,
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'data/custom_language_data.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
