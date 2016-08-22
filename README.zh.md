# zabbix_manager
## 语言选择

[中文](https://github.com/BillWang139967/zabbix_manager/blob/master/README.zh.md)
[English](https://github.com/BillWang139967/zabbix_manager/blob/master/README.md)

## 支持版本
> * zabbix2.4
> * zabbix3.0

## 【目录】
----

[0 简介](#0)  
........[0.1 自动化 ](#0.1)  
[1 ManagerTool 功能 ](#1)  
........[1.1 使用方法 ](#1.1)  
[2 zabbix api文件 ](#2)  
........[2.1 Hostgroups 管理 ](#2.1)  
........[2.2 usergroups 管理 ](#2.2)  
........[2.3 hosts 管理 ](#2.3)  
........[2.4 mediatype 管理 ](#2.4)  
[3 版本 ](#3)  


## 【正文】

<h2 name="0">0 简介</h2>

zabbix_manager 是个非常好的管理zabbix的软件

现在支持调用以下项
> * Templates 
> * Hostgroups
> * hosts
> * usergroup
> * user

<h3 name="0.1">0.1 自动化</h3>

**监控**

当我们计划监控某机器的时候，我们需要建立个主机组，然后导入到zabbix一些模板，最后添加机器即可

zabbix_manager是个非常好的选择，我们可以通过命令行做上面要做的事情

**报警**

当我们计划设置zabbix报警的时候。

第一：我们需要增加个报警方式，比如使用脚本进行邮件报警，使用脚本进行微信报警，等等。

第二：我们需要建立用户组以及某个用户

第三：对用户设置上报警方式，即报警时，zabbix给用户发送报警时的邮箱等等

最后：设置action

**报表**

日常需要做一些报表，同时这些报表需要使用excel交付，zabbix_manager
可以方便的直接导出报表，比如可以直接导出所有主机某个item在某个时间段的最小值、最大值、平均值

<h2 name="1">1 ManaterTool 功能</h2>

ManagerTool是交互式的管理配置界面，本目录下lib_zabbix里是api文件，api文件是保持有最新功能的

<h3 name="1.1">1.1 使用方法</h3>

修改配置文件

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
``` 
直接执行 the main.sh
```bash
$ sh main.sh

```
查看主机列表

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_get.jpg)

<h2 name="2">2 zabbix api文件</h2>

进入到lib_zabbix 目录后，lib_zabbix目录下也有个zabbix_config.ini文件，需要修改下
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
``` 
<h3 name="2.1">2.1 hostgroups 管理</h3>
(1)list hostgroups
```bash
#python -G

```
(2)add a hostgroup
```bash
# python zabbix_api.py --hostgroup_add "ceshi"

```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/hostgroup_add.jpg)
<h3 name="2.2">2.2 usergroups 管理</h3>
(1)list usergroups
```bash
#python --usergroup
```
(2)add a usergroup
```bash
# python zabbix_api.py --usergroup_add "op" "HostgroupName"
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/usergroup_add.jpg)
<h3 name="2.3">2.3 host 管理</h3>
(1)list hosts
```bash
#python -H --table
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_list.jpg)
<h3 name="2.4">2.4 mediatype 管理</h3>
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
<h2 name="3">3 版本发布</h2>
----
* v1.1.1，2016-08-22 新增：预估mysql存储大小
* v1.1.0，2016-07-14 release 1.1.0
* v1.0.8，2016-07-13 新增：导出报表
* v1.0.5，2016-06-19 新增：新增报警媒介类型管理
* v1.0.4，2016-06-18 新增：新增用户组和用户管理
* v1.0.3，2016-06-11 新增：可以方便的直接导出报表
* v1.0.2，2016-06-03 新增：新增交互模式
* v1.0.1，2016-04-16 新增：初次编写

## 致谢

1. 感谢南非蜘蛛的指导
