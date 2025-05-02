from odoo import models, fields, api
import smtplib, ssl
import imaplib
import email
from email.utils import parsedate_to_datetime

class Mailbox(models.Model):
    _name = 'webmail.mailbox'
    _description = 'Mailbox'

    name = fields.Char(string='Mailbox Name', required=True)
    smtp_server = fields.Char(string='SMTP Server', required=True)
    smtp_port = fields.Integer(string='SMTP Port', required=True, default=465)
    smtp_user = fields.Char(string='SMTP User', required=True)
    smtp_password = fields.Char(string='SMTP Password', required=True)
    imap_server = fields.Char(string='IMAP Server', required=True)
    imap_port = fields.Integer(string='IMAP Port', required=True, default=993)
    recipient_partner_ids = fields.Many2many('res.partner', string='Recipients')
    subject = fields.Char(string='Subject')
    body = fields.Text(string='Body')
    last_ssl_refresh = fields.Datetime(string='Last SSL Refresh')
    inbox_email_ids = fields.One2many('webmail.email', 'mailbox_id', string='Inbox Emails', domain="[('folder','=','INBOX')]")
    sent_email_ids = fields.One2many('webmail.email', 'mailbox_id', string='Sent Emails', domain="[('folder','=','Sent')]")
    draft_email_ids = fields.One2many('webmail.email', 'mailbox_id', string='Draft Emails', domain="[('folder','=','Drafts')]")

    def fetch_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_user, self.smtp_password)
            mail.select('inbox')
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            emails = []
            for e_id in email_ids[-10:]:  # Fetch the last 10 emails
                status, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append({
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'body': msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                })
            mail.logout()
            return emails
        except Exception as e:
            return str(e)

    def action_fetch_folder_emails(self):
        self.ensure_one()
        folder = self.env.context.get('folder', 'INBOX')
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_user, self.smtp_password)
            mail.select(folder)
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            for e_id in email_ids[-10:]:
                status, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject = msg['Subject'] or ''
                sender = msg['From'] or ''
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore') if msg.get_payload(decode=True) else ''
                # Create or update email record
                email_record = self.env['webmail.email'].create({
                    'mailbox_id': self.id,
                    'folder': folder,
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                })
                self.notify_new_email(email_record)
                # Notify the recipient user(s) if they exist in Odoo
                recipient_email = sender.lower().strip() if sender else ''
                partners = self.env['res.partner'].search([('email', '=', recipient_email)])
                for partner in partners:
                    user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
                    if user:
                        self.env['mail.message'].create({
                            'model': 'res.users',
                            'res_id': user.id,
                            'message_type': 'notification',
                            'body': f"New email from {sender}: {subject}",
                            'subject': "New Email in Webmail",
                            'author_id': user.partner_id.id,
                            'partner_ids': [(4, user.partner_id.id)],
                        })
            mail.logout()
        except Exception as e:
            pass

    def fetch_recent_emails(self):
        import datetime
        self.ensure_one()
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_user, self.smtp_password)
            mail.select('inbox')
            since_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%d-%b-%Y')
            status, messages = mail.search(None, f'(SINCE {since_date})')
            email_ids = messages[0].split()
            Email = self.env['webmail.email']
            for e_id in email_ids:
                status, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject = msg['Subject'] or ''
                sender = msg['From'] or ''
                date_str = msg['Date'] or ''
                try:
                    date = parsedate_to_datetime(date_str) if date_str else False
                    if date and date.tzinfo is not None:
                        date = date.replace(tzinfo=None)  # Make datetime naive
                except Exception:
                    date = False
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore') if msg.get_payload(decode=True) else ''
                # Check if this email already exists (by subject, sender, date)
                exists = Email.search([
                    ('mailbox_id', '=', self.id),
                    ('folder', '=', 'INBOX'),
                    ('subject', '=', subject),
                    ('sender', '=', sender),
                    ('date', '=', date)
                ], limit=1)
                if not exists:
                    email_record = Email.create({
                        'mailbox_id': self.id,
                        'folder': 'INBOX',
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'body': body,
                    })
                    self.notify_new_email(email_record)
                    # Notify the recipient user(s) if they exist in Odoo
                    recipient_email = sender.lower().strip() if sender else ''
                    partners = self.env['res.partner'].search([('email', '=', recipient_email)])
                    for partner in partners:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
                        if user:
                            self.env['mail.message'].create({
                                'model': 'res.users',
                                'res_id': user.id,
                                'message_type': 'notification',
                                'body': f"New email from {sender}: {subject}",
                                'subject': "New Email in Webmail",
                                'author_id': user.partner_id.id,
                                'partner_ids': [(4, user.partner_id.id)],
                            })
            mail.logout()
        except Exception as e:
            return str(e)

    def fetch_all_emails(self):
        import logging
        from email.header import decode_header
        import re
        self.ensure_one()
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_user, self.smtp_password)
            # Fetch all folders
            status, folders = mail.list()
            if status != 'OK':
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'IMAP folder list failed.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            Email = self.env['webmail.email']
            count = 0
            for folder_bytes in folders:
                folder_line = folder_bytes.decode()
                match = re.search(r'"([^"]+)"$', folder_line)
                folder = match.group(1) if match else folder_line.split()[-1]
                mail.select(f'"{folder}"')
                status, messages = mail.search(None, 'ALL')
                if status != 'OK':
                    continue
                email_ids = messages[0].split()
                for e_id in email_ids:
                    status, data = mail.fetch(e_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject_raw = msg['Subject'] or ''
                    subject, encoding = decode_header(subject_raw)[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8', errors='ignore')
                    sender = msg['From'] or ''
                    date_str = msg['Date'] or ''
                    try:
                        date = parsedate_to_datetime(date_str) if date_str else False
                        if date and date.tzinfo is not None:
                            date = date.replace(tzinfo=None)  # Make datetime naive
                    except Exception:
                        date = False
                    message_id = msg.get('Message-ID')
                    if msg.is_multipart():
                        body = ''
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))
                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                            elif ctype == 'text/html' and 'attachment' not in cdispo and not body:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore') if msg.get_payload(decode=True) else ''
                    domain = [('mailbox_id', '=', self.id), ('folder', '=', folder)]
                    if message_id:
                        domain.append(('body', '=', body))
                        domain.append(('subject', '=', subject))
                        domain.append(('sender', '=', sender))
                        if date:
                            domain.append(('date', '=', date))
                        domain.append(('body', '=', body))
                        domain.append(('message_id', '=', message_id))
                    else:
                        domain += [
                            ('subject', '=', subject),
                            ('sender', '=', sender),
                        ]
                        if date:
                            domain.append(('date', '=', date))
                        domain.append(('body', '=', body))
                    exists = Email.search(domain, limit=1)
                    if not exists:
                        email_record = Email.create({
                            'mailbox_id': self.id,
                            'folder': folder,
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'body': body,
                            'message_id': message_id,
                        })
                        self.notify_new_email(email_record)
                        count += 1
                        # Notify the recipient user(s) if they exist in Odoo
                        recipient_email = sender.lower().strip() if sender else ''
                        partners = self.env['res.partner'].search([('email', '=', recipient_email)])
                        for partner in partners:
                            user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
                            if user:
                                self.env['mail.message'].create({
                                    'model': 'res.users',
                                    'res_id': user.id,
                                    'message_type': 'notification',
                                    'body': f"New email from {sender}: {subject}",
                                    'subject': "New Email in Webmail",
                                    'author_id': user.partner_id.id,
                                    'partner_ids': [(4, user.partner_id.id)],
                                })
            mail.logout()
            # Show notify_info popup to the user who triggered the fetch
            self.env.user.notify_info(
                message=f"Fetched {count} new emails from all folders.",
                title="Webmail",
                sticky=False,
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Fetched {count} new emails from all folders.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            logging.exception('Error fetching all emails')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Error fetching emails: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def cron_refresh_ssl_connections(self):
        mailboxes = self.search([])
        for mailbox in mailboxes:
            try:
                context = ssl.create_default_context()
                with imaplib.IMAP4_SSL(mailbox.imap_server, mailbox.imap_port, ssl_context=context) as mail:
                    mail.login(mailbox.smtp_user, mailbox.smtp_password)
                # Use sudo to ensure write access and update in database
                mailbox.sudo().write({'last_ssl_refresh': fields.Datetime.now()})
            except Exception as e:
                pass

    @api.model
    def cron_fetch_all_emails(self):
        mailboxes = self.search([])
        for mailbox in mailboxes:
            try:
                mailbox.fetch_all_emails()
            except Exception:
                pass

    def test_connection(self):
        self.ensure_one()
        try:
            import imaplib
            import ssl
            context = ssl.create_default_context()
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port, ssl_context=context) as mail:
                mail.login(self.smtp_user, self.smtp_password)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Connection successful!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Connection failed: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def notify_new_email(self, email_record):
        # Send a bus notification to all users (or filter as needed)
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'webmail.new_email',
            {
                'subject': email_record.subject,
                'sender': email_record.sender,
                'date': str(email_record.date),
                'body': email_record.body[:200]  # Preview only
            }
        )