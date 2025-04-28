import socket
import ssl
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError

class MailAccount(models.Model):
    _name = 'mail.account'
    _description = 'Mail Account'

    name = fields.Char('Account Name')
    email = fields.Char('Email Address')
    imap_server = fields.Char('IMAP Server')
    imap_port = fields.Integer('IMAP Port')
    smtp_server = fields.Char('SMTP Server')
    smtp_port = fields.Integer('SMTP Port', default=465)
    username = fields.Char('Username')
    password = fields.Char('Password')

    def send_command(self, sock, command, wait_for="250"):
        sock.send((command + "\r\n").encode())
        response = sock.recv(1024).decode()
        if not response.startswith(wait_for):
            raise UserError(f"Unexpected SMTP response: {response}")
        return response

    def send_mail(self, to, subject, body_html):
        smtp_server = str(self.smtp_server or "").strip()
        smtp_port = int(self.smtp_port or 0)
        username = str(self.username or "").strip()
        password = str(self.password or "").strip()

        if not smtp_server or not smtp_port:
            raise UserError("SMTP Server settings missing. Please configure them.")

        context = ssl.create_default_context()
        with socket.create_connection((smtp_server, smtp_port)) as sock:
            with context.wrap_socket(sock, server_hostname=smtp_server) as server:

                server.recv(1024)  # Greeting
                self.send_command(server, "EHLO hibarr.de")

                self.send_command(server, "AUTH LOGIN", wait_for="334")
                server.send(base64.b64encode(username.encode()) + b"\r\n")
                server.recv(1024)
                server.send(base64.b64encode(password.encode()) + b"\r\n")
                server.recv(1024)

                self.send_command(server, f"MAIL FROM:<{username}>")
                self.send_command(server, f"RCPT TO:<{to}>")
                self.send_command(server, "DATA", wait_for="354")

                server.send(f"Subject: {subject}\r\nFrom: {username}\r\nTo: {to}\r\nContent-Type: text/html\r\n\r\n{body_html}\r\n.\r\n".encode())
                server.recv(1024)

                self.send_command(server, "QUIT")

    def test_smtp_connection(self):
        smtp_server = str(self.smtp_server or "").strip()
        smtp_port = int(self.smtp_port or 0)
        if not smtp_server or not smtp_port:
            raise UserError("SMTP Server settings missing.")

        try:
            context = ssl.create_default_context()
            with socket.create_connection((smtp_server, smtp_port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=smtp_server) as server:
                    server.recv(1024)  # Greeting
                    self.send_command(server, "EHLO hibarr.de")
                    self.send_command(server, "QUIT")
        except Exception as e:
            raise UserError(f"SMTP Test failed: {str(e)}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'SMTP Server connection successful.',
                'sticky': False,
            }
        }