{
    "name": "HIBARR Webmail (SocketSSL Version Fixed2)",
    "version": "2.2",
    "category": "Tools",
    "summary": "Webmail client with IMAP fetch, SMTP send via raw SSL Socket (fixed version 2) + SMTP Test Button",
    "author": "HIBARR Estates",
    "website": "https://hibarr.de",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/mail_models.xml",
        "security/ir.model.access.csv",
        "views/mail_account_views.xml",
        "views/mail_send_wizard_views.xml",
        "data/cron_jobs.xml"
    ],
    "installable": True,
    "application": True
}