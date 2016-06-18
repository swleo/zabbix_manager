# zabbix_manager
## Supported versions
> * zabbix2.4
> * zabbix3.0

## 【contents】
----

[0 introduction](#0)  
........[0.1 automation ](#0.1)  
[1 ManagerTool_function ](#1)  
........[1.1 usage ](#1.1)  
[2 zabbix_api ](#2)  
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
<h3 name="2.1">2.1 hostgroups manage</h3>
(1)list hostgroups
```bash
#python -G

```
(2)add a hostgroup
```bash
# python zabbix_api.py --hostgroup_add "ceshi"

```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/hostgroup_add.jpg)
<h3 name="2.2">2.2 usergroups manage</h3>
(1)list usergroups
```bash
#python --usergroup
```
(2)add a usergroup
```bash
# python zabbix_api.py --usergroup "op" "HostgroupName"
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/usergroup_add.jpg)
<h3 name="2.3">2.3 host manage</h3>
(1)list hosts
```bash
#python -H --table
```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_list.jpg)
<h2 name="3">3 version</h2>
----
* v1.0.4，2016-06-11 add usergroup manage
* v1.0.3，2016-06-11 add history_report
* v1.0.2，2016-06-03 Modify the command line in interactive mode
* v1.0.1，2016-04-16 First edit

## 致谢

1. 感谢南非蜘蛛的指导
