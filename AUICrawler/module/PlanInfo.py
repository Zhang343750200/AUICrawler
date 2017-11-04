# -*- coding:utf-8 -*-
import os
import datetime
from config import Setting
from DeviceInfo import Device
from script import Saver
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Plan:
    def __init__(self):
        self.coverageLevel = Setting.CoverageLevel
        self.runCaseTime = datetime.datetime.now()
        self.logPath = self.create_this_time_folder()
        self.deviceList = []
        self.deviceNum = str(len(self.deviceList))
        self.passedDevice = 0
        self.failedDevice = 0
        self.endTime = None
        self.resultHtml = '<a>测试结果</a>'

    # change the node info ,because the same type nodes has difference bounds.
    # the same type nodes need crawl once only

    # 创建目录保存结果
    def create_this_time_folder(self):
        path = os.getcwd() + '/result/' + self.runCaseTime.strftime('%Y%m%d%H%M%S')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    # 获取设备列表
    def get_device_list(self, app):
        device_list = []
        string = '	'
        outLine = os.popen('adb devices').readlines()
        for line in outLine:
            if string in line:
                device_id = line[0:line.index(string)]
                device = Device(self, device_id)
                device_list.append(device)
                if Setting.Login:
                    index = device_list.index(device)
                    accountList = Setting.AccountList[app.packageName]
                    device.update_device_account(accountList[index])
                    del index, accountList
                del device_id, device
            del line
        Saver.save_crawler_log(self.logPath, device_list)
        self.deviceList = device_list
        self.deviceNum = str(len(device_list))
        del device_list, string, outLine

    # 获取 device 实例列表
    def update_device_list(self, id_list):
        device_list = []
        for device_id in id_list:
            device = Device(self, device_id)
            device_list.append(device)
            del device_id, device
        self.deviceList = device_list
        self.deviceNum = str(len(device_list))
        del device_list
