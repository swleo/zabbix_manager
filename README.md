# zabbix_manager(server)
## language selection

+ [中文](https://github.com/BillWang139967/zabbix_manager/blob/master/README.zh.md)
+ [English](https://github.com/BillWang139967/zabbix_manager/blob/master/README.en.md)

## Supported versions
> * zabbix3.0

## 相关项目


> * zabbix安装-------------------------------------------------[zabbix_install](https://github.com/BillWang139967/zabbix_install)
> * zabbix报警工具---------------------------------------------[zabbix_alert](https://github.com/BillWang139967/zabbix_alert)
> * zabbix常用模板---------------------------------------------[zabbix_templates](https://github.com/BillWang139967/zabbix_templates)

**monitor**

When we plan to monitor, we must first create a host group, and then import some template, and finally add some hosts, zabbix_manager is a better choice

**alarm**

When we plan to use zabbix alarm . 
first, we need to add the alarm mode. 
the second, we need to create user groups and users.
the third, the user configuration of alarms. 
fourth, create action

**report**

Daily we need to export the report, use zabbix manager can export xls file using zabbix_manager will greatly save us time

## version
----
* v1.1.3，2016-09-09 add report_available2,排序可设置
* v1.1.2，2016-09-05 add zabbix_manager gui
* v1.1.1，2016-08-22 add mysql_quota
* v1.1.0，2016-07-14 release 1.1.0
* v1.0.8，2016-07-13 add report
* v1.0.6，2016-06-23 add rule and discovery manage
* v1.0.5，2016-06-19 add mediatype manage
* v1.0.4，2016-06-18 add usergroup manage
* v1.0.3，2016-06-11 add history_report
* v1.0.2，2016-06-03 Modify the command line in interactive mode
* v1.0.1，2016-04-16 First edit


## 参加步骤

* 在 GitHub 上 `fork` 到自己的仓库，然后 `clone` 到本地，并设置用户信息。
```
$ git clone https://github.com/BillWang139967/zabbix_manager.git
$ cd zabbix_manager
$ git config user.name "yourname"
$ git config user.email "your email"
```
* 修改代码后提交，并推送到自己的仓库。
```
$ #do some change on the content
$ git commit -am "Fix issue #1: change helo to hello"
$ git push
```
* 在 GitHub 网站上提交 pull request。
* 定期使用项目仓库内容更新自己仓库内容。
```
$ git remote add upstream https://github.com/BillWang139967/zabbix_manager.git
$ git fetch upstream
$ git checkout master
$ git rebase upstream/master
$ git push -f origin master
```
## 小额捐款

如果你觉得zabbix_manager对你有帮助, 可以对作者进行小额捐款(支付宝)

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/5.jpg)


## 致谢

1. 感谢南非蜘蛛的指导
