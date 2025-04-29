{
    'name': 'HIBARR Analysis Fields',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Analysis fields for HIBARR Estates',
    'description': """
        This module adds analysis functionality to contact information.
        Depends on custom_contact_info module for base contact fields.
    """,
    'author': 'HIBARR Estates',
    'depends': ['base', 'contacts', 'custom_contact_info','crm'],
    'data': [
        'views/analysis_view.xml',
        'views/lead_participant_views.xml',
        'data/checkboxes_data.xml',
        'data/property_feature_data.xml',
        'security/lead_salesperson_rule.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hibarr_analysis_fields/static/src/scss/crm_custom_fields.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
