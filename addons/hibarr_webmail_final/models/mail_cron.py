from odoo import models, api

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def fetch_new_emails_and_notify(self):
        mail_thread = self.env['mail.thread']
        new_emails = mail_thread._fetch_mail()  # Fetch all new emails
        if new_emails:
            for email in new_emails:
                # Example: Notify the user based on email recipient
                for recipient in email.partner_ids:
                    recipient.user_id.notify_info(
                        message=f"New Email: {email.subject}",
                        title="You've got a new email!",
                    )
