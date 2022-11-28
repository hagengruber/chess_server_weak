from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP
import random


class Mail:

    """Sends activation code via mail"""

    def __init__(self):

        # D O   N O T   T O U C H !!
        self.SMTPServer = 'smtp.ionos.de'
        self.sender = 'chess_dev-team@hagengruber.dev'
        self.USERNAME = "chess_dev-team@hagengruber.dev"
        # ToDo: Für starke Version: Passwort ist hardcoded im Klartext
        self.PASSWORD = "halonthxitol36598#!/89gotls"

    @staticmethod
    def create_code():
        # ToDo: Für starke Version: Code ist Bruteforcebar!
        return random.randint(1000, 99999)

    def send_mail(self, destination, code):

        """Sends mail"""

        destination = [destination]
        text_subtype = 'plain'
        subject = "Activation Code"

        content = ' Thanks for your registration! Your activation Code is: ' + str(code)

        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = self.sender

        try:

            conn = SMTP(self.SMTPServer)
            conn.set_debuglevel(False)
            conn.login(self.USERNAME, self.PASSWORD)
        except TimeoutError:
            return "Failed to send email. Make sure that you are connected to the Internet and your " \
                   "Firewall allows smtp connections"

        try:
            conn.sendmail(self.sender, destination, msg.as_string())
        finally:
            conn.quit()
            return None
