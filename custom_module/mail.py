#!/usr/bin/python
# coding=utf8
# Created by wangyikai at 18/07/12

from email.mime.text import MIMEText
from email.header import Header
import smtplib
import json


def send_mail(msg):
    with open("config/config.json") as jsonfile:
        config = json.load(jsonfile)
    mail_host = "smtp.exmail.qq.com"  # 设置服务器
    mail_user = "wangyikai@hortorgames.com"  # 用户名
    mail_pass = "gwEe62TYbGT3kKiV"  # 口令

    sender = 'wangyikai@hortorgames.com'
    receivers = config["MailReceivers"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(','.join(receivers), 'utf-8')

    subject = msg
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        return "邮件发送成功"
    except smtplib.SMTPException:
        return "Error: 无法发送邮件"
