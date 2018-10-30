#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19



from custom_module.transfer import Transfer
from custom_module.rollback import Rollback
from custom_module.mail import send_mail
from qcloud_module.clb import hortor_clb
import web
import commands
import os
import json



urls = (
    "/transfer", "transfer",
    "/rollback", "rollback"
)


class transfer:

    def __init__(self):
        self.mail = send_mail
        with open("config/config.json") as config:
            self.config = json.load(config)

    def POST(self):
        jsondata = web.input()
        try:
            assert jsondata["username"] == "kevin"
            assert jsondata["password"] == "kevin"
            assert str(jsondata["ProgramName"]) == str
        except:
            return "invalid parameter"
        obj = jsondata["ProgramName"]
        p_Transfer = Transfer(obj)
        p_hortor_clb = hortor_clb()






app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
