{
    'name': 'HIBARR Inteview Test',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Interview fields for HIBARR Estates',
    'description': """
        This module adds interview functionality to contact information.
    """,
    'author': 'HIBARR Estates',
    'depends': ['crm'],
    'data': [
        'views/interview_view.xml',
       
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
