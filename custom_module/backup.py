#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19

import os
import json
import commands
import time


class Backup(object):

    def __init__(self, obj):
        with open("config/config.json") as config:
            self.config = json.load(config)
            self.config = self.config["Program"][obj]
            self.obj = obj

    def backup(self, server):
        """
        :param server: 接收一个正式服服务器地址作为备份源
        """
        # 创建备份目录
        t = time.strftime("%Y%m%d%H%M%S")
        for i in self.config["DirType"]:
            try:
                os.makedirs("%s/%s/%s" % (self.config["OpsServerInfo"]["BackupDir"], t, i))
            except OSError:
                pass
        # 备份正式服文件到本地
        for i in self.config["DirType"]:
            commands.getoutput("scp %s@%s:%s/%s/* %s/%s/%s" % (
                self.config["ReleaseServerInfo"]["SshUser"], server, self.config["ReleaseServerInfo"]["ServerDir"], i,
                self.config["OpsServerInfo"]["BackupDir"],
                t, i
            ))
        commands.getoutput("cd %s/%s && tar zcf %s.tar.gz %s" % (
        self.config["OpsServerInfo"]["BackupDir"], t, self.obj, " ".join(self.config["DirType"])))
        print  "Backup Success ( %s )" % t
        return "Backup Success ( %s )" % t
