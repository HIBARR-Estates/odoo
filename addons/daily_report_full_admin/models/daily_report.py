from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class DailyEmployeeReport(models.Model):
    _name = "daily.employee.report"
    _description = "Daily Employee Report"
    _order = "report_date desc"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, default=lambda self: self.env.user.employee_id.id)
    report_date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    report_text = fields.Text(string="Report", required=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")

    hr_rating = fields.Selection(
        selection=[
            ('0', 'Not Rated'),
            ('1', 'Unsatisfactory'),
            ('2', 'Adequate'),
            ('3', 'Satisfactory'),
            ('4', 'Good'),
            ('5', 'Very good')
        ],
        string='HR Rating',
        index=True,
        default='0')
    hr_comment = fields.Text(string="HR Comment")
    supervisor_rating = fields.Selection(
        selection=[
            ('0', 'Not Rated'),
            ('1', 'Unsatisfactory'),
            ('2', 'Adequate'),
            ('3', 'Satisfactory'),
            ('4', 'Good'),
            ('5', 'Very good')
        ],
        string='Manager Rating',
        index=True,
        default='0')
    supervisor_comment = fields.Text(string="Manager Comment")

    submitted_at = fields.Datetime(string="Submitted At", default=fields.Datetime.now)
    is_late = fields.Boolean(string="Submitted Late", compute="_compute_is_late", store=True)

    @api.depends("submitted_at", "report_date")
    def _compute_is_late(self):
        for rec in self:
            if rec.submitted_at and rec.report_date:
                deadline = datetime.combine(rec.report_date + timedelta(days=1), datetime.strptime("09:00", "%H:%M").time())
                rec.is_late = rec.submitted_at > deadline

    @api.constrains("report_date")
    def _check_submission_time(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.report_date == now.date() and now.hour < 12:
                raise ValidationError(_("Reports can only be submitted after 12:00 on the same day."))

    _sql_constraints = [
        ('employee_date_uniq', 'unique(employee_id, report_date)', 'You have already submitted a report for this day.')
    ]



    @api.model
    def create(self, vals):
        user = self.env.user
        employee = user.employee_id

        # Gruppenprüfung
        is_admin = user.has_group('base.group_system')
        is_hr = user.has_group('hr.group_hr_user')
        is_supervisor = any(r.employee_id.parent_id.user_id == user for r in self)

        now = fields.Datetime.now()
        today = now.date()
        report_date = fields.Date.from_string(vals.get('report_date')) if vals.get('report_date') else today

        # Zeitgrenzen für normale Benutzer
        limit_start = datetime.combine(today, datetime.min.time()).replace(hour=12)
        limit_end = datetime.combine(report_date + timedelta(days=1), datetime.min.time()).replace(hour=9)

        # Benutzer ist kein Admin, kein HR, kein Supervisor
        if not (is_admin or is_hr or is_supervisor):
            if 'employee_id' in vals and vals['employee_id'] != employee.id:
                raise ValidationError("You can only create reports for yourself.")

            if now < limit_start or now > limit_end:
                raise ValidationError("You can only submit your report between 12:00 PM and 09:00 AM next day.")

        return super().create(vals)



    def write(self, vals):
        user = self.env.user
        is_admin = user.has_group('base.group_system')
        is_hr = user.has_group('hr.group_hr_user')
        is_supervisor = any(r.employee_id.parent_id.user_id == user for r in self)
        employee = self.env.user.employee_id

        for record in self:
            # Verhindere, dass normale User die Bewertung setzen
            if not (is_hr or is_supervisor or is_admin):
                if 'supervisor_rating' in vals or 'supervisor_comment' in vals or 'hr_rating' in vals or 'hr_comment' in vals:
                    raise ValidationError("You are not allowed to modify supervisor or HR ratings.")
            # Supervisor darf nur für seine eigenen Mitarbeiter bewerten
            if is_supervisor and not is_hr:
                if 'supervisor_rating' in vals or 'supervisor_comment' in vals:
                    if record.employee_id.parent_id.user_id != user:
                        raise ValidationError("Supervisors can only rate employees from their own department.")
                if 'hr_rating' in vals or 'hr_comment' in vals:
                    raise ValidationError("Supervisors cannot modify HR fields.")

            # HR darf keine Supervisor-Felder bearbeiten
            if is_hr and not is_supervisor:
                if 'supervisor_rating' in vals or 'supervisor_comment' in vals:
                    raise ValidationError("HR cannot modify supervisor feedback.")

        return super().write(vals)


from odoo import models, fields

class HREmployee(models.Model):
    _inherit = "hr.employee"

    daily_report_required = fields.Boolean(string="Daily Report Required", default=False)
    daily_report_notify_time = fields.Float(string="Notification Time (24h format)", default=8.5,
                                            help="Time of day (e.g., 8.5 for 08:30) when the employee should be reminded.")
