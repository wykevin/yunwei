#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19

from qcloud_module.cvm import CvmClass
from qcloud_module.clb import ClbClass
import time
import requests


class ElasticScalingClass(CvmClass, ClbClass):

    def __init__(self, obj, config, obj_elastic_host_configure):
        """
        :param obj:
        :param config:
        """
        CvmClass.__init__(self)
        ClbClass.__init__(self)
        self.obj = obj
        self.config = config
        self.obj_elastic_host_configure = obj_elastic_host_configure

    def add_host(self, instace_count):
        """
        :param instace_count:
        :return:
        """
        try:
            # make elastic instance
            elastic_instance_id_list = self.make_instances(instace_count, self.obj_elastic_host_configure)
            time.sleep(60)

            # get elastic instance info
            elastic_instance_info = self.get_instances_info_by_id(elastic_instance_id_list)

            # get elastic instance info for running state
            running_elastic_instance_info = {}
            for instance_id, state_wanip in elastic_instance_info.iteritems():
                if state_wanip[0] == "RUNNING":
                    running_elastic_instance_info[instance_id] = state_wanip[1]
            print "running instance: %s" % len(running_elastic_instance_info)

            # get health elastic instance list
            health_elastic_instance_id_list = []
            for instance_id, wanip in running_elastic_instance_info.iteritems():
                check_result = self.check_elastic_instance_health(wanip)
                # try 2 times
                if check_result[0] != 200:
                    time.sleep(10)
                    check_result = self.check_elastic_instance_health(wanip)
                    if check_result[0] != 200:
                        continue
                health_elastic_instance_id_list.append(instance_id)
            print "health instance: %s" % len(health_elastic_instance_id_list)

            # add health elastic instance to lb
            for lb_id in self.config["LoadBalancerId"]:
                self.registerInstancesWithLoadBalancer(lb_id, health_elastic_instance_id_list, 100)
            return "add host is success"
        except Exception as e:
            return "add host is false: %s" % e

    def reduce_host(self, instance_count):
        pass

    def check_elastic_instance_health(self, instance_ip):
        """
        :param instance_ip:
        :return:
        """
        url = "http://%s%s" % (instance_ip, self.config["LBHealthUrl"])
        req = requests.get(url, timeout=5)
        return req.status_code, req.text
