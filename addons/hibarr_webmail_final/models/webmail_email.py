from odoo import models, fields

class WebmailEmail(models.Model):
    _name = 'webmail.email'
    _description = 'Webmail Email'

    mailbox_id = fields.Many2one('webmail.mailbox', string='Mailbox', ondelete='cascade')
    folder = fields.Char(string='Folder')
    subject = fields.Char(string='Subject')
    sender = fields.Char(string='Sender')
    body = fields.Text(string='Body')
    date = fields.Datetime(string='Date')
    is_read = fields.Boolean(string='Read', default=False)
    message_id = fields.Char(string='Message-ID', index=True)
    thread_id = fields.Many2one('webmail.email.thread', string='Thread')
    parent_id = fields.Many2one('webmail.email', string='Parent Email')
    child_ids = fields.One2many('webmail.email', 'parent_id', string='Replies')
    # Add more fields as needed (e.g., recipients, attachments)

    def mark_as_read(self):
        self.ensure_one()
        self.is_read = True

    def mark_as_unread(self):
        self.ensure_one()
        self.is_read = False

    def action_delete(self):
        self.ensure_one()
        self.unlink()

    def action_view_email(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'webmail.email',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def reply(self):
        self.ensure_one()
        # Open the send.mail popup with pre-filled recipient, subject, and quoted body
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'send.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_recipient_email': self.sender,
                'default_subject': f"Re: {self.subject}",
                'default_body': f"<br><br>----- Original Message -----<br>{self.body}",
            },
        }

    def forward(self):
        self.ensure_one()
        # Open the send.mail popup with pre-filled subject and quoted body
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'send.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': f"Fwd: {self.subject}",
                'default_body': f"<br><br>----- Forwarded Message -----<br>{self.body}",
            },
        }