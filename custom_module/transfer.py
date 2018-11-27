#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19


from backup import BackupClass
import commands
import threading


class TransferClass(object):

    def __init__(self, obj, config):
        self.obj = obj
        self.config = config
        self.bak = BackupClass(self.obj, self.config)

    def copy_file_2_ops(self):
        # 传包到运维发布服并且创建预发布压缩包
        try:
            # 打包
            status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && tar zcf %s.tar.gz %s'" % (
                self.config["TestServerInfo"]["SshUser"], self.config["TestServerInfo"]["SshIp"],
                self.config["TestServerInfo"]["ServerDir"], self.obj, " ".join(self.config["DirType"])))
            assert status_code == 0, msg
            # 传包
            status_code, msg = commands.getstatusoutput("scp %s@%s:%s/%s.tar.gz %s" % (
                self.config["TestServerInfo"]["SshUser"], self.config["TestServerInfo"]["SshIp"],
                self.config["TestServerInfo"]["ServerDir"], self.obj,
                self.config["OpsServerInfo"]["PreReleaseDir"]
            ))
            assert status_code == 0, msg
            # 删除
            status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && rm -rf %s.tar.gz'" % (
                self.config["TestServerInfo"]["SshUser"], self.config["TestServerInfo"]["SshIp"],
                self.config["TestServerInfo"]["ServerDir"], self.obj))
            assert status_code == 0, msg
            return "copy_file_2_ops success"
        except Exception as e:
            return "copy_file_2_ops error", e

    def copy_file_2_release(self, release_host_list):
        try:
            copy_file_2_ops_resuslt = self.copy_file_2_ops()
            assert copy_file_2_ops_resuslt == "copy_file_2_ops success", copy_file_2_ops_resuslt
            backup_result = self.bak.backup(release_host_list[0])
            assert "Backup Success" in backup_result, backup_result
            self.release_host_list_iter = iter(release_host_list)
            self.thread_result = []
            self.make_threads(self.transfer_thread)
            assert self.thread_result.count(True) == len(release_host_list), self.thread_result
            return "transfer success\n", backup_result
        except Exception as e:
            return "transfer error", e

    def scp(self, instance_ip):
        status_code, msg = commands.getstatusoutput("scp %s/%s.tar.gz %s@%s:%s" % (
            self.config["OpsServerInfo"]["PreReleaseDir"], self.obj, self.config["ReleaseServerInfo"]["SshUser"],
            instance_ip, self.config["ReleaseServerInfo"]["ServerDir"]))
        if status_code != 0:
            return False, msg
        status_code, msg = commands.getstatusoutput("ssh %s@%s 'cd %s && tar zxf %s.tar.gz'" % (
            self.config["ReleaseServerInfo"]["SshUser"], instance_ip, self.config["ReleaseServerInfo"]["ServerDir"],
            self.obj))
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
