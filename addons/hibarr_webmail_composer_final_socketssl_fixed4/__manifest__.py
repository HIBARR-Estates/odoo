{
    'name': 'HIBARR Webmail Composer',
    'version': '1.0',
    'summary': 'Send emails via your own IMAP/SMTP accounts',
    'description': 'Manage webmail accounts, send emails using SSL socket connection.',
    'category': 'Tools',
    'author': 'HIBARR Development',
    'website': 'https://hibarr.de',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_account_views.xml',
        'views/menu.xml',
        'data/cron_jobs.xml'
    ],
    'installable': True,
    'application': True,
}