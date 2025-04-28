{
    "name": "HIBARR Webmail (SocketSSL Version Fixed3)",
    "version": "2.3",
    "category": "Tools",
    "summary": "Webmail client with IMAP fetch, SMTP send via raw SSL Socket (final fixed3) + SMTP Test Button + Mail Accounts Menu",
    "author": "HIBARR Estates",
    "website": "https://hibarr.de",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/mail_models.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/mail_account_views.xml",
        "views/mail_send_wizard_views.xml",
        "data/cron_jobs.xml"
    ],
    "installable": True,
    "application": True
}