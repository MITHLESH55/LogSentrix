import smtplib

server = smtplib.SMTP("smtp.gmail.com",587)
server.starttls()

server.login("yourgmail@gmail.com","your_app_password")

server.sendmail(
"yourgmail@gmail.com",
"yourgmail@gmail.com",
"Subject: Test Mail\n\nHello from LogSentrix"
)

print("Mail Sent")