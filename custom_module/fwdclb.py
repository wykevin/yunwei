#!/usr/bin/python
# coding=utf8
# Created by wangyikai at 18/07/12


from qcloud_module.sign import signture
import requests
import sys
from time import sleep


class hortor_fwdclb(signture):

    def __init__(self):
        signture.__init__(self)
        self.url = "https://lb.api.qcloud.com/v2/index.php?"

    def describeForwardLBBackends(self, lb_id, listener_id_list, pro_url, domain):
        params = self.params.copy()
        params["Action"] = "DescribeForwardLBBackends"
        params["loadBalancerId"] = lb_id
        for i in range(len(listener_id_list)):
            params["listenerIds.%s" % i] = listener_id_list[i]
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        if result["code"] != 0:
            print "DescribeForwardLBListeners error code : %s \n error log : %s" % (
                result["code"], result["codeDesc"])
            sys.exit(1)
        listenerIdInfos = result["data"]
        backendsServerList = []
        for listenerIdInfo in listenerIdInfos:
            bkd_List = []
            for rule in listenerIdInfo["rules"]:
                if rule["url"] == pro_url and rule["domain"] == domain:
                    for backends in rule["backends"]:
                        bkd_instanceName = backends["instanceName"]
                        bkd_unInstanceId = backends["unInstanceId"]
                        bkd_lanIp = backends["lanIp"]
                        bkd_port = backends["port"]
                        bkd_List.append((bkd_instanceName, bkd_unInstanceId, bkd_lanIp, bkd_port))
            backendsServerList.append(bkd_List)

        # 如果有两个监听器, 那就判断一下每个监听器下的主机列表是否相同
        if len(listener_id_list) == 2:
            assert backendsServerList[0] == backendsServerList[1]

        return backendsServerList[0]

    def modifyForwardSeventhBackends(self, lb_id, listener_id, pro_url, domain, instance_id_list, weight):
        print "%s - %s set weight to %s" % (lb_id, listener_id, weight)
        params = self.params.copy()
        params["Action"] = "ModifyForwardSeventhBackends"
        params["loadBalancerId"] = lb_id
        params["listenerId"] = listener_id
        params["domain"] = domain
        params["url"] = pro_url
        for i in range(len(instance_id_list)):
            params["backends.%s.instanceId" % i] = instance_id_list[i][1]
            params["backends.%s.port" % i] = instance_id_list[i][3]
            params["backends.%s.weight" % i] = weight
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        if result["code"] != 0:
            print "ModifyForwardSeventhBackends error code : %s \n error log : %s" % (
            result["code"], result["codeDesc"])
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
