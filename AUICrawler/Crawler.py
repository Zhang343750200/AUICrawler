#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import getopt
import sys
import threading

from config import Setting
from module.CrawledApp import App
from module.PlanInfo import Plan
from runner import runner
from script import Saver
from script import MailSender

plan = Plan()

opts, args = getopt.getopt(sys.argv[1:], "aicsjklud:t:r:p:")
for op, value in opts:
    if op == "-a": # 遍历模式  Random ／ Normal ／ Activity
        Setting.CrawlModel = 'Activity'
    elif op == "-u": # 执行前卸载、安装App
        Setting.UnInstallApk = True
        Setting.InstallApk = True
    elif op == "-i": # 进入主页面前也会有一些可遍历的页面／控件，设置是否遍历
        Setting.RunInitNodes = True
    elif op == '-c': # 执行初始化Robotium Case
        Setting.RunInitCase = True
    elif op == '-s': # 只保存有效遍历操作截图
        Setting.SaveScreen = True
    elif op == '-j': # 保存还原控件显示、跳出App等非有效遍历截图
        Setting.SaveJumpOutScreen = True
    elif op == '-k': # Crash/ANR 后继续执行
        Setting.KeepRun = True
    elif op == '-l': # 遍历过程中登录
        Setting.Login = True
    elif op == '-d': # 指定单设备/多设备列表
        device_list = []
        if ',' in value:
            device_list = value.split(',')
        else:
            device_list.append(value)
        plan.update_device_list(device_list)
    elif op == '-t': # 开启限时模式，调整遍历限时时间，单位分钟
        Setting.TimeModel = 'Limit'
        Setting.LimitTime = int(value)
    elif op == '-r': # 设置随机遍历覆盖程度
        Setting.CoverageLevel = float(value)
        if Setting.CrawlModel == 'Normal':
            Setting.CrawlModel = 'Random'
    elif op == '-p': # 指定被测app、被测app的测试app
        if ',' in value:
            apk_list = []
            apk_list = value.split(',')
            Setting.ApkPath = apk_list[0]
            Setting.TestApkPath = apk_list[1]
        else:
            Setting.ApkPath = value

app = App(plan)

if len(plan.deviceList) == 0:
    plan.get_device_list(app)
elif Setting.Login:
    device_list = plan.deviceList
    for device in device_list:
        index = device_list.index(device)
        accountList = Setting.AccountList[app.packageName]
        device.update_device_account(accountList[index])
        del device, index, accountList

threads = []

for device in plan.deviceList:
    thread = threading.Thread(target=runner.run_test, args=(plan, app, device))
    threads.append(thread)
for th in threads:
    th.start()
for th in threads:
    th.join()

plan.endTime = datetime.datetime.now()
Saver.save_crawl_result(plan, app)
MailSender.send_mail(plan)
