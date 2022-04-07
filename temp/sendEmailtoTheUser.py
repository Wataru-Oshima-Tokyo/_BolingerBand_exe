import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import constVariables


class Email():
    def __init__(self):
        self.my_addr = constVariables.CVAL.my_addr
        self.my_pass = constVariables.CVAL.my_pass
        

    def create_message(self, subject, body_txt):
        msg = MIMEText(body_txt)
        msg["Subject"] = subject
        msg["From"] = self.my_addr
        msg["To"] = self.my_addr
        return msg

    def send_mail(self,msg):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.my_addr, self.my_pass)
            server.send_message(msg)

    def main(self, content, title):
        now = datetime.now()
        todays_date = str(now.strftime("%Y年%m月%d日%H:%M:%S ")) 
        title = todays_date + str(title)
        showResult = content
        if showResult !="":
            msg = self.create_message(title, showResult)
            self.send_mail(msg)
            print("successfully emailed to the user")
    
if __name__ == "__main__":
    email = Email()
