#!/usr/local/bin/python
# coding:utf-8
# 这个脚本是一个发送邮件的脚本
import smtplib
import string
#定义邮件host
HOST = "smtp.163.com"
#定义邮件主题
SUBJECT = "这是在测试python发送邮件"
#定义邮件发件人
FROM = "qi138138lin@163.com"
#定义邮件收件人
TO = "164158310@qq.com"

Text = "这是邮件的内容"

BODY = string.join((
    "From:%s" % FROM,
    "To:%s" % TO,
    "Subject:%s" % SUBJECT,
    "",
    Text
    ),
    "\r\n"
)

smtp = smtplib.SMTP()
smtp.connect(HOST, 25)
smtp.starttls()
smtp.login("*", "***")
smtp.sendmail(FROM, [TO], BODY)
smtp.quit()