{
    "name": "Daily Employee Report Full",
    "version": "1.0",
    "category": "Human Resources",
    "summary": "Fully featured daily employee report with ratings, deadlines, dashboards, and translations",
    "author": "HIBARR Estates",
    "depends": ["base", "hr", "web"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "views/daily_report_menu.xml",
        "views/daily_report_views.xml"
    ],
    "installable": True,
    "application": True
}
