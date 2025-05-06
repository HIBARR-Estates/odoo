from odoo import models, fields, api
import re
from datetime import datetime, timedelta

class Email(models.Model):
    _name = 'webmail.email'
    _description = 'Webmail Email'

    mail_account_id = fields.Many2one('mail.account', string='Mail Account', required=True)
    mailbox_id = fields.Many2one('webmail.mailbox', string='Mailbox', ondelete='cascade')
    folder = fields.Char(string='Folder')
    subject = fields.Char(string='Subject')
    body = fields.Text(string='Body')
    date = fields.Datetime(string='Date')
    sender = fields.Char(string='Sender')
    recipient = fields.Char(string='Recipient')
    message_id = fields.Char(string='Message-ID', index=True)
    thread_id = fields.Many2one('webmail.email', string='Parent Email (Thread)')
    child_ids = fields.One2many('webmail.email', 'thread_id', string='Thread Replies')
    attachment_ids = fields.Many2many('ir.attachment', 'webmail_email_attachment_rel', 'email_id', 'attachment_id', string='Attachments')
    is_read = fields.Boolean(string='Read', default=False)
    parent_id = fields.Many2one('webmail.email', string='Parent Email')
    sender_name = fields.Char(string='Sender Name', compute='_get_sender_name')
    formatted_date = fields.Char(string='Formatted Date', compute='_get_formatted_date')
    reply_count = fields.Integer(string='Reply Count', compute='_compute_reply_count')

    @api.depends('child_ids')
    def _compute_reply_count(self):
        for record in self:
            record.reply_count = len(record.child_ids)

    def action_reply(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reply to Email',
            'res_model': 'send.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_thread_id': self.id,
                'default_subject': f'Re: {self.subject or ""}',
                'default_recipient_email': self.sender,
                'default_mail_account_id': self.mail_account_id.id,
                'default_folder': self.folder,
                'default_body': f"<br><br>----- Original Message -----<br>{self.body}",
            },
        }

    def reply(self):
        return self.action_reply()

    def forward(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'send.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': f'Fwd: {self.subject}',
                'default_body': f'<br><br>----- Forwarded Message -----<br>{self.body}',
                'default_mail_account_id': self.mail_account_id.id,
            },
        }

    @api.depends('sender')
    def _get_sender_name(self):
        for record in self:
            match = re.match(r'(.*) <(.*)>', record.sender or '')
            record.sender_name = match.group(1) if match else record.sender

    @api.depends('date')
    def _get_formatted_date(self):
        for record in self:
            date = record.date
            if not date:
                record.formatted_date = ''
                continue
            today = datetime.today()
            if date.date() == today.date():
                record.formatted_date = date.strftime('%I:%M %p')
            elif date.date() == (today - timedelta(days=1)).date():
                record.formatted_date = date.strftime('%d %b')
            else:
                record.formatted_date = date.strftime('%d %b %Y')

    def mark_as_read(self):
        self.ensure_one()
        self.is_read = True

    def mark_as_unread(self):
        self.ensure_one()
        self.is_read = False

    def action_delete(self):
        self.ensure_one()
        self.unlink()
        return {
            'type': 'ir.actions.act_window_close'
        }

    def action_view_email(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'webmail.email',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }