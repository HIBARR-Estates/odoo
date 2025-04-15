{
    'name': 'Analysis Fields',
    'version': '18.0.1.0.0',
    'summary': 'Adds analysis fields to various models',
    'description': """
        This module adds analysis fields to various models for better data analysis
        and reporting capabilities.
    """,
    'author': 'HIBARR Estates',
    'website': 'https://hibarr.net',
    'category': 'Tools',
    'depends': [
        'base',
        'crm',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/analysis_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'analysis_fields/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 10,
} 