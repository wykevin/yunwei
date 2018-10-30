#!/usr/bin/python
# coding=utf8
# Created by wangyikai at 18/07/12


from qcloud_module.sign import signture
import requests
import sys
from time import sleep


class hortor_clb(signture):

    def __init__(self):
        signture.__init__(self)
        self.url = "https://lb.api.qcloud.com/v2/index.php?"

    def describeLoadBalancerBackends(self, loadBalancerId):
        """
        :param loadBalancerId: LB实例ID
        :return: LB下挂载的主机列表
        """
        params = self.params.copy()
        params["Action"] = "DescribeLoadBalancerBackends"
        params["loadBalancerId"] = loadBalancerId
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        if result["code"] != 0:
            print "DescribeLoadBalancerBackends error code : %s \n error log : %s" % (
                result["code"], result["codeDesc"])
            sys.exit(1)
        rsList = []
        for i in result["backendSet"]:
            rsList.append((i["instanceName"], i["unInstanceId"], i["lanIp"]))
        return rsList

    def modifyLoadBalancerBackends(self, loadBalancerId, instanceId_list, weight):
        """
        :param loadBalancerId: LB实例ID
        :param instanceId_list: 实例ID列表
        :param weight: 权重值
        :return: 修改权重的结果
        """
        print "%s set weight to %s" % (loadBalancerId, weight)
        params = self.params.copy()
        params["Action"] = "ModifyLoadBalancerBackends"
        params["loadBalancerId"] = loadBalancerId
        for i in range(len(instanceId_list)):
            params["backends.%s.instanceId" % i] = instanceId_list[i]
            params["backends.%s.weight" % i] = weight
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        if result["code"] != 0:
            print "ModifyLoadBalancerBackends error code : %s \n error log : %s" % (result["code"], result["codeDesc"])
            sys.exit(1)
        sleep(5)
        count = 0
        while True:
            count += 1
            status = self.describeLoadBalancersTaskResult(result["requestId"])
            if status != 0:
                if count < 5:
                    print "try %s times" % count
                    sleep(5)
                else:
                    print "set weight false , status: %s , requestId: %s" % (status, result["requestId"])
                    sys.exit(1)
            else:
                return result

    def describeLoadBalancersTaskResult(self, requestId):
        """
        :param requestId: 修改权重操作的任务ID
        :return: 该任务ID的执行结果
        """
        params = self.params.copy()
        params["Action"] = "DescribeLoadBalancersTaskResult"
        params["requestId"] = requestId
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        if result["code"] != 0:
            print "DescribeLoadBalancersTaskResult error code : %s \n error log : %s" % (
                result["code"], result["codeDesc"])
            sys.exit(1)
        return result["data"]["status"]
