#!/usr/bin/python
# coding=utf8
# Created by wangyikai at 18/07/12


from qcloud_module.clb import ClbClass
import commands
import threading
import time


class DeployClass(ClbClass):

    def __init__(self, obj, config, thread_number, update_host_number):
        ClbClass.__init__(self)
        self.obj = obj
        self.config = config
        self.lbId = self.config["LoadBalancerId"]
        self.thread_number = thread_number
        self.update_host_number = update_host_number
        self.ssh_user = self.config["ReleaseServerInfo"]["SshUser"]

    def update(self, instance_ip):
        # 通用的更新方法，先重启然后再查看状态
        commands.getoutput(
            "ssh %s@%s 'sudo supervisorctl restart %s'" % (self.ssh_user, instance_ip, self.obj))
        time.sleep(3)
        status_code, msg = commands.getstatusoutput(
            "ssh %s@%s 'sudo supervisorctl status %s'" % (self.ssh_user, instance_ip, self.obj))
        print msg
        if status_code != 0:
            return False, msg
        # 重启过后必须是RUNNING状态才会返回True
        if "RUNNING" in msg:
            return True
        else:
            return False, msg

    def make_threads(self, func):
        threads = []
        for i in range(self.thread_number):
            t = threading.Thread(target=func, args=(i,))
            threads.append(t)
            t.start()
        for i in threads:
            i.join()

    def thread_update(self, thread_name):
        try:
            while True:
                instance_ip = self.host_group_ip_iter.next()
                update_result = self.update(instance_ip)
                self.thread_result.append(update_result)
        except StopIteration:
            pass

    def update_one(self, gray_host=None):
        try:
            assert type(self.lbId) == list, "lb type error"
            host_list = self.describeLoadBalancerBackends(self.lbId[0])
            if gray_host == None:
                host = host_list[0]
            else:
                for i in host_list:
                    if gray_host == i[2]:
                        host = i
                        break
                    else:
                        host = False
                assert host != False, "host %s not found" % gray_host
            print "start update", host[0]
            for lb_id in self.lbId:
                self.modifyLoadBalancerBackends(lb_id, [host[1]], 0)
            self.update(host[2])
            for lb_id in self.lbId:
                self.modifyLoadBalancerBackends(lb_id, [host[1]], 10)
        except Exception as e:
            return "update_one error", e

    def update_all(self):
        try:
            assert type(self.lbId) == list, "lb type error"
            if len(self.lbId) == 1:
                host_list = self.describeLoadBalancerBackends(self.lbId[0])
            elif len(self.lbId) == 2:
                host_list = self.describeLoadBalancerBackends(self.lbId[0])
                host_list1 = self.describeLoadBalancerBackends(self.lbId[1])
                assert host_list == host_list1, "host_list != host_list1"
            else:
                raise ValueError, "config.json : lb_id most support 2 values"

            for i in range(0, len(host_list), self.update_host_number):
                host_group = host_list[i:i + self.update_host_number]
                instance_name_list = [i[0] for i in host_group]  # 定义实例名称列表
                instance_id_list = [i[1] for i in host_group]  # 定义实例ID列表
                instance_ip_list = [i[2] for i in host_group]  # 定义实例IP列表
                print "start update", instance_name_list
                for lb_id in self.lbId:
                    self.modifyLoadBalancerBackends(lb_id, instance_id_list, 0)
                self.thread_result = []
                self.host_group_ip_iter = iter(instance_ip_list)
                self.make_threads(self.thread_update)
                assert self.thread_result.count(True) == len(host_group), "update error"
                for lb_id in self.lbId:
                    self.modifyLoadBalancerBackends(lb_id, instance_id_list, 100)

        except Exception as e:
            return "update_all error", e
