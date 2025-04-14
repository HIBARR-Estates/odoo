{
    'name': 'Custom CRM Extensions',
    'version': '18.0.1.0.0',
    'summary': 'Extends CRM with additional personalization fields',
    'description': """
        Adds custom fields to CRM leads for personal information, partner & children details
        and enhances the lead views with additional address information.
        
        Features:
        - Personal Information fields (age, employment, occupation)
        - Partner Information fields
        - Children Information fields
        - Enhanced address fields
        - Language preferences
    """,
    'author': 'HIBARR Estates',
    'website': 'https://crm.hibarr.net',
    'category': 'CRM',
    'depends': [
        'crm',
        'base_address_extended',  # For enhanced address handling
        'contacts',  # For partner related fields
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/custom_language_data.xml',
        'views/crm_lead_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_crm_2/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 10,
}