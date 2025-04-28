import socket
import ssl
import base64
from odoo import models, fields, api
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            raise Exception(f"Unexpected response: {response}")
        return response

    def send_mail(self, to, subject, body_html):
        smtp_server = self.smtp_server
        smtp_port = self.smtp_port
        username = self.username
        password = self.password

        context = ssl.create_default_context()
        with socket.create_connection((smtp_server, smtp_port)) as sock:
            with context.wrap_socket(sock, server_hostname=smtp_server) as server:

                server.recv(1024)  # Greeting
                self.send_command(server, f"EHLO hibarr.de")

                self.send_command(server, "AUTH LOGIN", wait_for="334")
                server.send(base64.b64encode(username.encode()) + b"\r\n")
                server.recv(1024)
                server.send(base64.b64encode(password.encode()) + b"\r\n")
                server.recv(1024)

                self.send_command(server, f"MAIL FROM:<{username}>")
                self.send_command(server, f"RCPT TO:<{to}>")
                self.send_command(server, "DATA", wait_for="354")

                message = MIMEMultipart('alternative')
                message['Subject'] = subject
                message['From'] = username
                message['To'] = to
                part2 = MIMEText(body_html, 'html')
                message.attach(part2)

                server.send((message.as_string() + "\r\n.\r\n").encode())
                server.recv(1024)

                self.send_command(server, "QUIT")