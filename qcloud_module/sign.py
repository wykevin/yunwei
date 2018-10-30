#!/usr/bin/python
# coding:utf8
# Created at 18/07/12 by wangyikai


import json
import random
import time
import base64
import hashlib
import hmac
import urllib


class signture(object):

    def __init__(self):
        with open("config/config.json") as secret:
            self.secret = json.load(secret, encoding="utf8")

        self.params = {
            "Region": self.secret["Region"],
            "SecretId": self.secret["SecretId"],
            "SignatureMethod": "HmacSHA256"
        }

    def sign(self, url, params):
        params["Nonce"] = random.randint(1, 99999)
        params["Timestamp"] = str(time.time()).split(".")[0]
        argument = ""
        for i in sorted(params.keys()):
            argument += "%s=%s&" % (i, params[i])
        argument = argument[0:-1]
        signstr = "GET%s%s" % (url.replace("https://", ""), argument)
        signature = base64.b64encode(
            hmac.new(self.secret["SecretKey"].encode("utf8"), signstr, digestmod=hashlib.sha256).digest())
        signature = urllib.quote(signature)
        requests_url = "%s%s&Signature=%s" % (url, argument, signature)
        return requests_url
