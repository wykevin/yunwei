#!/usr/bin/python
# coding:utf8
# Created by wangyikai at 18/10/19


from custom_module.transfer import TransferClass
from custom_module.rollback import RollbackClass
from custom_module.backup import BackupClass
from qcloud_module.clb import ClbClass
from custom_module.deploy import DeployClass
from custom_module.elasticscaling import ElasticScalingClass
from custom_module.pirate import PirateClass

import web
import json

urls = (
    "/transfer", "Transfer",
    "/get_backup_list", "GetBackupList",
    "/rollback", "Rollback",
    "/deploy", "Deploy",
    "/elastic_scaling", "ElasticScaling"
)


class ConfigClass(object):

    def __init__(self):
        with open("config/config.json") as config:
            self.config = json.load(config)
            self.username = self.config["Username"]
            self.password = self.config["Password"]


class Transfer(ConfigClass):

    def __init__(self):
        ConfigClass.__init__(self)

    def POST(self):
        data = web.input()
        # POST参数判断
        try:
            assert data["UserName"] == self.username, "UserName Error"
            assert data["PassWord"] == self.password, "PassWord Error"
            assert data["ProgramName"] in self.config["Program"].keys(), "ProgramName Not Found"
            self.config = self.config["Program"][data["ProgramName"]]
        except Exception as e:
            return "Invalid Parameter", e
        obj = data["ProgramName"]

        # 实例化 Clb 类 得到后端主机列表
        clb = ClbClass()
        host_list = clb.describeLoadBalancerBackends(self.config["LoadBalancerId"][0])
        host_list = [i[2] for i in host_list]

        # 实例化Transfer类 并传输包到正式服
        tf = TransferClass(obj, self.config)
        result = tf.copy_file_2_release(host_list)

        return result


class GetBackupList(ConfigClass):

    def __init__(self):
        ConfigClass.__init__(self)

    def POST(self):
        data = web.input()
        # POST参数判断
        try:
            assert data["UserName"] == self.username, "UserName error"
            assert data["PassWord"] == self.password, "PassWord error"
            assert data["ProgramName"] in self.config["Program"].keys(), "ProgramName Not Found"
            self.config = self.config["Program"][data["ProgramName"]]
        except Exception as e:
            return "Invalid Parameter", e
        obj = data["ProgramName"]

        # 实例化Backup类 获取备份目录列表
        b = BackupClass(obj, self.config)
        result = b.getbackup()

        return result


class Rollback(ConfigClass):

    def __init__(self):
        ConfigClass.__init__(self)

    def POST(self):
        data = web.input()
        # POST参数判断
        try:
            assert data["UserName"] == self.username, "UserName error"
            assert data["PassWord"] == self.password, "PassWord error"
            assert data["ProgramName"] in self.config["Program"].keys(), "ProgramName Not Found"
            assert len(data["Version"]) != 0, "Version Error"
            self.config = self.config["Program"][data["ProgramName"]]
        except Exception as e:
            return "Invalid Parameter", e
        obj = data["ProgramName"]

        # 实例化hortor_clb类 得到后端主机列表
        clb = ClbClass()
        host_list = clb.describeLoadBalancerBackends(self.config["LoadBalancerId"][0])
        host_list = [i[2] for i in host_list]

        # 实例化Rollback类 传输备份到正式服
        r = RollbackClass(obj, self.config)
        result = r.rollback(data["Version"], host_list)

        return result


class Deploy(ConfigClass):

    def __init__(self):
        ConfigClass.__init__(self)

    def POST(self):
        data = web.input()
        # POST参数判断
        try:
            assert data["UserName"] == self.username, "UserName error"
            assert data["PassWord"] == self.password, "PassWord error"
            assert data["DeployType"] in ["update_all", "update_one"], "Invalid Parameter: DeployType"
            data["ThreadCount"] = int(data["ThreadCount"])
            data["UpdateHostCount"] = int(data["UpdateHostCount"])
            assert type(data["ThreadCount"]) == int and 0 < data[
                "ThreadCount"] < 20, "Invalid Parameter: ThreadCount"
            assert type(data["UpdateHostCount"]) == int and 0 < data[
                "UpdateHostCount"] < 20, "Invalid Parameter: UpdateHostCount"
            assert data["ProgramName"] in self.config["Program"].keys(), "ProgramName Not Found"
            self.config = self.config["Program"][data["ProgramName"]]
        except Exception as e:
            return "Invalid Parameter:", e
        obj = data["ProgramName"]

        # 实例化Deploy类 灰度更新 或 全量更新
        d = DeployClass(obj, self.config, data["ThreadCount"], data["UpdateHostCount"])
        if data["DeployType"] == "update_one":
            result = d.update_one()
        elif data["DeployType"] == "update_all":
            result = d.update_all()
        else:
            result = "DeployType Not Found"

        return result


class ElasticScaling(ConfigClass, PirateClass):

    def __init__(self):
        ConfigClass.__init__(self)
        PirateClass.__init__(self)

    def POST(self):
        data = web.input()
        # POST参数判断
        try:
            assert data["UserName"] == self.username, "UserName error"
            assert data["PassWord"] == self.password, "PassWord error"
            assert data["ProgramName"] in self.config["Program"].keys(), "ProgramName Not Found"
            assert data["ScalingType"] in ["add", "reduce"]
            data["ScalingHostCount"] = int(data["ScalingHostCount"])
            self.config = self.config["Program"][data["ProgramName"]]
        except Exception as e:
            return "Invalid Parameter:", e
        obj = data["ProgramName"]

        try:
            with open("config/elasticHostConfigure/%s.json" % obj) as elasticHostConfigure:
                obj_elastic_host_configure = json.load(elasticHostConfigure)
        except Exception as e:
            return "elastic host configure not found",e

        # 实例化 ElasticScalingClass 类 增加机器
        es = ElasticScalingClass(obj, self.config, obj_elastic_host_configure)
        if data["ScalingType"] == "add":
            if obj == "pirate":
                lock_result = self.lock_gm()
                assert lock_result[0] == 200, "lock pirate gm error,%s" % lock_result[1]
                result = es.add_host(data["ScalingHostCount"])
                unlock_result = self.unlock_gm()
                assert unlock_result[0] == 200, "unlock pirate gm error,%s" % unlock_result[1]
            else:
                result = es.add_host(data["ScalingHostCount"])
        else:
            result = "not support"

        return result


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
