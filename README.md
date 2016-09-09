# zabbix_manager(server)
## language selection

+ [中文](https://github.com/BillWang139967/zabbix_manager/blob/master/README.zh.md)
+ [English](https://github.com/BillWang139967/zabbix_manager/blob/master/README.md)

## Supported versions
> * zabbix3.0

## 【contents】
----

[0 introduction](#0)  
........[0.1 automation ](#0.1)  
[1 ManagerTool_function ](#1)  
........[1.1 usage ](#1.1)  
[2 zabbix_api ](#2)  
........[2.1 Hostgroups management ](#2.1)  
........[2.2 usergroups management ](#2.2)  
........[2.3 hosts management ](#2.3)  
........[2.4 mediatype management ](#2.4)  
[3 version ](#3)  


## 【body】

<h2 name="0">0 introduction</h2>

This tool is very useful for the  management zabbix.
It current supports the following:
> * Templates 
> * Hostgroups
> * hosts
> * usergroup
> * user

<h3 name="0.1">0.1 automation</h3>

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

<h2 name="1">1 ManaterTool Function</h2>

<h3 name="1.1">1.1 usage</h3>

Configure zabbix_manager
First you should configure zabbix_config.ini to works with appropriate zabbix server and use right credentials.
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
``` 
run the main.sh
Just run: 
```bash
$ sh main.sh

```
list the hosts

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_get.jpg)

<h2 name="2">2 zabbix_api</h2>
First you should configure zabbix_config.ini to works with appropriate zabbix server and use right credentials.
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
``` 
<h3 name="2.1">2.1 hostgroups management</h3>
(1)list hostgroups
```bash
#python -G

```
(2)add a hostgroup
```bash
# python zabbix_api.py --hostgroup_add "ceshi"

```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/hostgroup_add.jpg)
<h3 name="2.2">2.2 usergroups management</h3>
(1)list usergroups
```bash
#python --usergroup
```
(2)add a usergroup
```bash
# python zabbix_api.py --usergroup_add "op" "HostgroupName"
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/usergroup_add.jpg)
<h3 name="2.3">2.3 hosts management</h3>
(1)list hosts
```bash
#python -H --table
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_list.jpg)
<h3 name="2.4">2.4 mediatype management</h3>
(1)list mediatype
```bash
#python --mediatype --table
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/mediatype_list.jpg)

(2)add a mediatype
```bash
# python zabbix_api.py --mediatype_add mediaName scriptName
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/mediatype_add.jpg)

(3)delete a mediatype
```bash
# python zabbix_api.py --mediatype_del mediaName
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/mediatype_del.jpg)
<h2 name="3">3 version</h2>
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
