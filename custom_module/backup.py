#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19

import os
import commands
import time


class BackupClass(object):

    def __init__(self, obj, config):
        self.obj = obj
        self.config = config

    def backup(self, server):
        """
        :param server: 接收一个正式服服务器地址作为备份源
        """
        # 创建备份目录
        try:
            t = time.strftime("%Y%m%d%H%M%S")
            os.makedirs("%s/%s" % (self.config["OpsServerInfo"]["BackupDir"], t))
            # 备份正式服文件到本地
            status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && tar zcf %s.tar.gz %s'" % (
                self.config["ReleaseServerInfo"]["SshUser"], server,
                self.config["ReleaseServerInfo"]["ServerDir"], self.obj, " ".join(self.config["DirType"])))
            assert status_code == 0, msg
            status_code, msg = commands.getstatusoutput("scp %s@%s:%s/%s.tar.gz %s/%s" % (
                self.config["ReleaseServerInfo"]["SshUser"], server,
                self.config["ReleaseServerInfo"]["ServerDir"], self.obj,
                self.config["OpsServerInfo"]["BackupDir"], t
            ))
            assert status_code == 0, msg
            print "Backup Success ( %s )" % t
            return "Backup Success ( %s )" % t
        except Exception as e:
            return "Backup error", e

    def getbackup(self):
        backup_list = os.listdir(self.config["OpsServerInfo"]["BackupDir"])
        return {"backup_list": sorted(backup_list)}
