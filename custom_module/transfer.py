#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19


from backup import Backup
import json
import commands
import threading


class Transfer(object):

    def __init__(self, obj):
        with open("config/config.json") as config:
            self.obj = obj
            self.config = json.load(config)
            self.config = self.config["Program"][obj]

    def copy_file_2_ops(self):
        # 传包到运维发布服并且创建预发布压缩包
        try:
            for i in self.config["DirType"]:
                commands.getoutput("scp %s@%s:%s/%s/* %s/%s/" % (
                    self.config["TestServerInfo"]["SshUser"], self.config["TestServerInfo"]["SshIp"],
                    self.config["TestServerInfo"]["ServerDir"], i,
                    self.config["OpsServerInfo"]["PreReleaseDir"], i
                ))
                status_code, msg = commands.getstatusoutput("cd %s && tar zcf %s.tar.gz %s" % (
                    self.config["OpsServerInfo"]["PreReleaseDir"], self.obj, " ".join(self.config["DirType"])))
                assert status_code == 0, msg
            print "copy_file_2_ops success"
            return "copy_file_2_ops success"
        except Exception as e:
            return "copy_file_2_ops error", e

    def copy_file_2_release(self, release_host_list):
        assert self.copy_file_2_ops() == "copy_file_2_ops success"
        b = Backup(self.obj)
        backup_result = b.backup(release_host_list[0])
        self.release_host_list_iter = iter(release_host_list)
        self.thread_result = []
        try:
            self.make_threads(self.transfer_thread)
            assert self.thread_result.count(True) == len(release_host_list), self.thread_result
            return "transfer success\n",backup_result
        except Exception as e:
            return "transfer error", e

    def scp(self, instance_ip):
        status_code, msg = commands.getstatusoutput("scp %s/%s.tar.gz %s@%s:%s" % (
            self.config["OpsServerInfo"]["PreReleaseDir"], self.obj, self.config["ReleaseServerInfo"]["SshUser"],
            instance_ip, self.config["ReleaseServerInfo"]["ServerDir"]))
        print msg
        if status_code != 0:
            return False, msg
        status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && tar zxf %s.tar.gz'" % (
        self.config["ReleaseServerInfo"]["SshUser"], instance_ip, self.config["ReleaseServerInfo"]["ServerDir"],
        self.obj))
        print msg
        if status_code != 0:
            return False, msg
        return True

    def make_threads(self, func):
        threads = []
        for i in range(5):
            t = threading.Thread(target=func, args=(i,))
            threads.append(t)
            t.start()
        for i in threads:
            i.join()

    def transfer_thread(self, thread_name):
        try:
            while True:
                instance_ip = self.release_host_list_iter.next()
                transfer_result = self.scp(instance_ip)
                self.thread_result.append(transfer_result)
        except StopIteration:
            pass

