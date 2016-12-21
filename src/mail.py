#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socket, imaplib, smtplib
from debug import Debugger


class MailBox2(object):
    def __init__(self, addr_imap="", port_imap="", addr_smtp="", port_smtp=""):
        self.addr_imap = addr_imap
        self.port_imap = port_imap
        self.addr_smtp = addr_smtp
        self.port_smtp = port_smtp

        self.debugger = Debugger(True)

    def login(self, username, password):
        self.username = username
        self.password = password

        if not self.connect_imap():
            self.debugger.print_error("LOGIN ERROR!", "mail.MailBox.login()", "Server connection unestablished")
            return False

        try:
            self.server_imap.login(self.username, self.password)
        except:
            self.debugger.print_error("LOGIN ERROR!", "mail.MailBox.login()", "Poor internet connection")
            return False

    def connect_imap(self):
        try:
            self.server_imap = imaplib.IMAP4_SSL(self.addr_imap, self.port_imap)
        except:
            self.debugger.print_error("SERVER ERROR!", "mail.MailBox.connect_imap()", "Poor internet connection")
            return False

        return True

    def select_folder(self, folder_name):
        return self.server_imap.select(folder_name)

    def unseen_ids(self):
        self.select_folder("INBOX")
        # server.search(None, 'unseen') returns ('OK', [b'818 819']) so
        r, d = self.server_imap.search(None, 'unseen')
        mail_list = d[0].decode("utf-8").split(' ')
        return mail_list

class MailBox(object):
    def __init__(self, uname="", passwd="", imapsw="", imapprt="", smtpsw="", smtpprt=""):
        self.username = uname
        self.password = passwd
        self.imap_server = imapsw
        self.imap_port = imapprt
        self.smtp_server = smtpsw
        self.smtp_port = smtpprt

    # IMAP
    def check_new_mail(self):
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            server.login(self.username, self.password)
        except:
            print("[!] Cannot connect imap server. Probably poor internet connection problem.")
            return -1

        server.select('INBOX')
        # server.search(None, 'unseen') returns ('OK', [b'818 819']) so
        new_mail = server.search(None, 'unseen')[1][0]
        new_mail = new_mail.decode("utf-8")

        # close & logout
        server.close()
        server.logout()

        # Means no new mail
        if len(new_mail) == 0:
            return 0

        new_mail = new_mail.split(' ')
        return len(new_mail)

    def check_imap_response(self):
        socket.setdefaulttimeout(2)
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        except:
            socket.setdefaulttimeout(5)
            return "Server"
        try:
            server.login(self.username, self.password)
        except:
            socket.setdefaulttimeout(5)
            return "Username/Password"

        socket.setdefaulttimeout(5)
        return "valid"

    # SMTP
    def check_smtp_response(self):
        socket.setdefaulttimeout(2)
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        except:
            socket.setdefaulttimeout(5)
            return "Server"
        try:
            server.login(self.username, self.password)
        except:
            socket.setdefaulttimeout(5)
            return "Username/Password"

        socket.setdefaulttimeout(5)
        return "valid"
