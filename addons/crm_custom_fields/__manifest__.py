{
    'name': 'CRM Custom Fields',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Custom fields for CRM leads',
    'description': """
        This module adds custom fields to CRM leads for better customer information management.
    """,
    'author': 'HIBARR Estates',
    'depends': ['crm'],
    'data': [
        
        'views/crm_lead_custom_view.xml',
        'data/custom_language_data.xml',
        'data/property_features_data.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'crm_custom_fields/static/src/scss/crm_custom_fields.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
