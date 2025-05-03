{
    "name": "HIBARR Webmail Final",
    "version": "1.0",
    "depends": ["base"],
    "author": "HIBARR",
    "category": "Tools",
    "data": [
        "security/ir.model.access.csv",
        "views/mailbox_views.xml",
        
        "views/mail_account_views.xml",
        "views/send_mail_view.xml",
        "views/menu.xml",
        "wizards/mail_send_wizard_views.xml",
        "data/cron.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "hibarr_webmail_final/static/src/css/summernote_custom.css",
            "hibarr_webmail_final/static/src/js/webmail_notification.js",
        ],
    },
    "installable": True,
    "application": True
}