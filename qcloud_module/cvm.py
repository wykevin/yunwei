#!/usr/bin/python
# coding:utf8
# Created at 18/07/13 by wangyikai


from qcloud_module.sign import signture
import requests


class hortor_cvm(signture):

    def __init__(self):
        signture.__init__(self)
        self.url = "https://cvm.tencentcloudapi.com/?"

    def describeInstances(self, cvmLanIpList):
        """
        :param cvmLanIpList: 云主机内网IP列表
        :return: 对应云主机实例ID列表
        """
        params = self.params.copy()
        params["Action"] = "DescribeInstances"
        params["Version"] = "2017-03-12"
        params["Filters.0.Name"] = "private-ip-address"
        for i in range(len(cvmLanIpList)):
            params["Filters.0.Values.%s" % i] = cvmLanIpList[i]
        url = self.sign(self.url, params)
        result = requests.get(url, timeout=15).json()
        cvmInstancesIdList = []
        for i in result["Response"]["InstanceSet"]:
            cvmInstancesIdList.append(i["InstanceId"])
