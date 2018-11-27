#!/usr/bin/python
# coding:utf8
# Created at 18/07/13 by wangyikai


from qcloud_module.sign import signture
import requests


class CvmClass(signture):

    def __init__(self):
        signture.__init__(self)
        self.cvm_url = "https://cvm.tencentcloudapi.com/?"

    def get_instances_id_by_ip(self, cvm_ip_list):
        """
        :param cvm_ip_list: 云主机内网IP列表
        :return: 对应云主机实例ID列表
        """
        params = self.params.copy()
        params["Action"] = "DescribeInstances"
        params["Version"] = "2017-03-12"
        params["Filters.0.Name"] = "private-ip-address"
        for i in range(len(cvm_ip_list)):
            params["Filters.0.Values.%s" % i] = cvm_ip_list[i]
        url = self.sign(self.cvm_url, params)
        result = requests.get(url, timeout=15).json()
        cvm_id_list = []
        for i in result["Response"]["InstanceSet"]:
            cvm_id_list.append(i["InstanceId"])
        return cvm_id_list

    def get_instances_info_by_id(self, cvm_id_list):
        """
        :param cvm_id_list: 云主机实例ID列表
        :return: 对应云主机实例内网IP列表
         """
        if len(cvm_id_list) == 0:
            assert False, "empty host list"
        params = self.params.copy()
        params["Action"] = "DescribeInstances"
        params["Version"] = "2017-03-12"
        for i in range(len(cvm_id_list)):
            params["InstanceIds.%s" % i] = cvm_id_list[i]
        url = self.sign(self.cvm_url, params)
        result = requests.get(url, timeout=15).json()
        instance_info = {}
        for i in result["Response"]["InstanceSet"]:
            instance_info[i["InstanceId"]] = [i["InstanceState"], i["PublicIpAddresses"][0]]
        return instance_info

    def make_instances(self, instance_count, obj_elastic_host_configure):
        params = self.params.copy()
        # 参数合并
        params = dict(params.items() + obj_elastic_host_configure.items())
        params["InstanceCount"] = instance_count
        url = self.sign(self.cvm_url, params)
        result = requests.get(url, timeout=15).json()
        instance_id_list = result["Response"]["InstanceIdSet"]
        return instance_id_list
