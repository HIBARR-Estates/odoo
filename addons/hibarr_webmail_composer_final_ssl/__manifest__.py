{
    "name": "HIBARR Webmail (SSL Version)",
    "version": "1.9",
    "category": "Tools",
    "summary": "Webmail client with IMAP fetch, SMTP send (SMTP_SSL)",
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