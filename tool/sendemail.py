import smtplib
from email.mime.text import MIMEText
_user = "wangxiao084@163.com"
_pwd  = "w123456"
_to   = ""

# json str

def send(message):
    msg = MIMEText(message or "Error Message")
    msg["Subject"] = "New message from portal"
    msg["From"] = _user
    msg["To"] = _to
    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()
        print("Success!")
    except smtplib.SMTPException:
        print ("Falied")
