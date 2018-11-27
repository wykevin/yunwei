#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19


import commands
import threading
import os


class RollbackClass(object):

    def __init__(self, obj, config):
        self.obj = obj
        self.config = config

    def rollback(self, version, release_host_list):
        try:
            self.version = version
            assert os.path.isfile("%s/%s/%s.tar.gz" % (
                self.config["OpsServerInfo"]["BackupDir"], version, self.obj)) == True, "backup file not found"
            self.release_host_list_iter = iter(release_host_list)
            self.thread_result = []
            self.make_threads(self.rollback_thread)
            assert self.thread_result.count(True) == len(release_host_list), self.thread_result
            return "backup transfer success"
        except Exception as e:
            return "backup transfer error", e

    def copy_backup_2_release(self, instance_ip):
        try:
            status_code, msg = commands.getstatusoutput("scp %s/%s/%s.tar.gz %s@%s:%s" % (
                self.config["OpsServerInfo"]["BackupDir"], self.version, self.obj,
                self.config["ReleaseServerInfo"]["SshUser"],
                instance_ip, self.config["ReleaseServerInfo"]["ServerDir"]))
            assert status_code == 0, msg
            status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && tar zxf %s.tar.gz'" % (
                self.config["ReleaseServerInfo"]["SshUser"], instance_ip, self.config["ReleaseServerInfo"]["ServerDir"],
                self.obj))
            assert status_code == 0, msg
            return True
        except Exception as e:
            return "%s rollback false: " % instance_ip, e

    def make_threads(self, func):
        threads = []
        for i in range(5):
            t = threading.Thread(target=func, args=(i,))
            threads.append(t)
            t.start()
        for i in threads:
            i.join()

    def rollback_thread(self, thread_name):
        try:
            while True:
                instance_ip = self.release_host_list_iter.next()
                transfer_result = self.copy_backup_2_release(instance_ip)
                self.thread_result.append(transfer_result)
        except StopIteration:
            pass
