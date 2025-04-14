{
    'name': 'Custom CRM Extensions',
    'version': '1.0',
    'summary': 'Extends CRM with additional personalization fields',
    'description': """
        Adds custom fields to CRM leads for personal information, partner & children details
        and enhances the lead views with additional address information.
    """,
    'author': 'HIBARR Estates',
    'website': 'https://crm.hibarr.net',
    'category': 'CRM',
    'depends': ['crm'],
    'data': [
        'data/custom_language_data.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}