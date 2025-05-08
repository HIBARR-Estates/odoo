{
    'name': 'Hibarr Webmail',
    'version': '1.0',
    'summary': 'A powerful webmail application for Odoo',
    'sequence': -100,
    'category': 'Tools',
    'author': 'HIBARR Estate',
    'website': 'https://hibarr.de',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    "description": """
        HIBARR Webmail Final is a comprehensive webmail solution for Odoo, providing features such as email management, SMTP configuration, and user-friendly interfaces.
    """,
    "images": ["static/description/banner.png"],

    "data": [
        "security/ir.model.access.csv",
        "views/mailbox_views.xml",
        "views/mail_account_views.xml",
        "views/send_mail_view.xml",
        "views/menu.xml",
        "views/menu.xml",
        "wizards/mail_send_wizard_views.xml",
        "data/cron.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "hibarr_webmail_final/static/src/css/summernote_custom.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": True,
    }