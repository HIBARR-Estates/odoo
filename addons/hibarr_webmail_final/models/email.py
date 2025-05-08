from odoo import models, fields, api
import re
from datetime import datetime, timedelta
from markupsafe import Markup, escape
from bs4 import BeautifulSoup, Doctype
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

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
    rendered_body = fields.Html(string='Rendered Body', compute='_compute_rendered_body')
    reply_count = fields.Integer(string='Reply Count', compute='_compute_reply_count')

    @api.depends('body', 'attachment_ids')
    def _compute_rendered_body(self):
        for record in self:
            if record.body:
                # Parse the email body with BeautifulSoup
                soup = BeautifulSoup(record.body, 'lxml')

                # Clean and fix HTML (remove invalid or redundant tags)
                for tag in soup.find_all(True):
                    if tag.name.lower() in ['style', 'script', 'meta', 'link']:
                        tag.decompose()  # Remove these tags
                    elif tag.name.lower() in ['html', 'head', 'body', 'footer']:
                        tag.unwrap()  # Remove outermost tags

                # Ensure a proper DOCTYPE (optional)
                clean_html = BeautifulSoup("<!DOCTYPE html><html><head></head><body></body></html>", 'lxml')
                clean_html.html.body.append(soup)

                # Convert any text URLs to clickable links
                for text in clean_html.find_all(text=True):
                    if text.parent.name not in ['a', 'script', 'style']:
                        new_text = re.sub(
                            r'(https?://[^\s]+)',
                            r'<a href="\1" target="_blank">\1</a>',
                            text
                        )
                        text.replace_with(new_text)

                # Add attachments if any
                if record.attachment_ids:
                    attachment_section = clean_html.new_tag("div")
                    attachment_section.append(clean_html.new_tag("br"))
                    attachment_section.append(clean_html.new_tag("strong", string="Attachments:"))
                    attachment_section.append(clean_html.new_tag("br"))

                    for attachment in record.attachment_ids:
                        attachment_link = clean_html.new_tag(
                            "a",
                            href=f"/web/content/{attachment.id}",
                            target="_blank"
                        )
                        attachment_link.string = attachment.name
                        attachment_section.append(attachment_link)
                        attachment_section.append(clean_html.new_tag("br"))

                    clean_html.html.body.append(attachment_section)

                # Final rendered body
                record.rendered_body = Markup(str(clean_html))
            else:
                record.rendered_body = ""

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
        return {'type': 'ir.actions.act_window_close'}

    def action_view_email(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'webmail.email',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
