#!/usr/bin/python3
# -*- coding: utf-8 -*-
import view, mail, sys, os
from config import *
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

class Fmail(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = view.Ui_Fmail()
        self.ui.setupUi(self)
        self.init_fmail()

    def init_fmail(self):
        self.num_of_unseen = -1
        self.ui.btn_save_account.clicked.connect(self.save_account)
        self.ui.chb_automail.stateChanged.connect(self.handle_automail)

        if conf['settings']['num_of_mailbox']:
            self.ui.lne_imap_server.setText(conf["mailbox0"]["imap_server"])
            self.ui.lne_imap_port.setText(conf["mailbox0"]["imap_port"])
            self.ui.lne_smtp_server.setText(conf["mailbox0"]["smtp_server"])
            self.ui.lne_smtp_port.setText(conf["mailbox0"]["smtp_port"])
            self.ui.lne_username.setText(conf["mailbox0"]["username"])
            self.ui.lne_password.setText("password")
            self.init_mail()

    def init_mail(self):
        self.mailbox = mail.MailBox()

        self.load_mailbox_settings(self.mailbox, "mailbox0")

        self.automail_thread = MailThread(self.mailbox)
        self.automail_thread.mailsignal.connect(self.handle_new_mail)

        self.automail_timer = QTimer()
        self.automail_freq = 5000  # check mail once in X second
        self.automail_timer.timeout.connect(self.automail_thread.start)

    def handle_new_mail(self, new_mail):
        if self.num_of_unseen == -1:
            os.system( 'notify-send -i ~/app-icon.png "Unseen Mail" "You have '+ str(new_mail) +' unseen mail."' )
            self.num_of_unseen = new_mail
        elif self.num_of_unseen < new_mail:
            os.system('notify-send -i ~/app-icon.png "New Mail !" "You have new mail !"')
            self.num_of_unseen = new_mail

        self.ui.statusBar.showMessage("You have " + str(new_mail) + " unseen messages", 2000)

    "Developer & Contact" "furkan.tokac@metu.edu.tr\nfurkantokac.blogspot.com"
    def handle_automail(self, state):
        if state:
            self.automail_timer.start(self.automail_freq)
            self.ui.statusBar.showMessage("Automail checking is ENABLED", 1500)
            print("[+] Automail checking is ENABLED")
        else:
            self.automail_timer.stop()
            self.ui.statusBar.showMessage("Automail checking is DISABLED", 1500)
            print("[-] Automail checking is DISABLED")

    def save_account(self):
        tmp_mailbox = mail.MailBox()
        tmp_username = self.ui.lne_username.text()
        tmp_password = self.ui.lne_password.text()
        tmp_imap_server = self.ui.lne_imap_server.text()
        tmp_imap_port = self.ui.lne_imap_port.text()
        tmp_smtp_server = self.ui.lne_smtp_server.text()
        tmp_smtp_port = self.ui.lne_smtp_port.text()
        self.load_mailbox_settings(tmp_mailbox, '', tmp_username, tmp_password, tmp_imap_server, tmp_imap_port,
                                   tmp_smtp_server, tmp_smtp_port)
        response = tmp_mailbox.check_imap_response()

        if response != "valid":
            QMessageBox.warning(self, "Connection Error", response + " is not valid. Please check your informations.",
                                QMessageBox.Close)
            print("[!] " + response + " is not valid. Not saved")
            return

        mailbox_id = 'mailbox' + str(conf["settings"]["num_of_mailbox"])
        conf[mailbox_id] = {}
        conf[mailbox_id]["username"] = tmp_username
        conf[mailbox_id]["password"] = encrypt(tmp_password)
        conf[mailbox_id]["imap_server"] = tmp_imap_server
        conf[mailbox_id]["imap_port"] = tmp_imap_port
        conf[mailbox_id]["smtp_server"] = tmp_smtp_server
        conf[mailbox_id]["smtp_port"] = tmp_smtp_port
        conf[mailbox_id]["auto_check_freq"] = 60
        # bool(self.ui.chb_startup_automail.checkState())
        conf["settings"]["num_of_mailbox"] += 1
        save_conf()
        # self.init_mail

    def load_mailbox_settings(self, mailbox, mailbox_id="", uname="", pwd="", imapsw="", imapprt="", smtpsw="",
                              smtpprt=""):
        if mailbox_id:
            mailbox.username = conf[mailbox_id]["username"]
            mailbox.password = decrypt(conf[mailbox_id]["password"])
            mailbox.imap_server = conf[mailbox_id]["imap_server"]
            mailbox.imap_port = conf[mailbox_id]["imap_port"]
            mailbox.smtp_server = conf[mailbox_id]["smtp_server"]
            mailbox.smtp_port = conf[mailbox_id]["smtp_port"]
        else:
            mailbox.username = uname
            mailbox.password = pwd
            mailbox.imap_server = imapsw
            mailbox.imap_port = imapprt
            mailbox.smtp_server = smtpsw
            mailbox.smtp_port = smtpprt


class MailThread(QThread):
    mailsignal = pyqtSignal(int)

    def __init__(self, mailbox):
        QThread.__init__(self)

        self.mailbox = mailbox

    def run(self):
        self.check_mail()

    def check_mail(self):
        new_mail = self.mailbox.check_new_mail()
        self.mailsignal.emit(new_mail)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = Fmail()
    # myapp.setWindowIcon(QIcon(dirs["app_icon"]))
    myapp.show()
    sys.exit(app.exec_())
