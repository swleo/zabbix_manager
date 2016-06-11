# zabbix_manager
## Supported versions
> * zabbix2.4
> * zabbix3.0

## 【contents】
----

[0 introduction](#0)  
[1 ManagerTool_function ](#1)  
........[1.1 usage ](#1.1)  
[2 version ](#3)  


## 【body】

<h2 name="0">0 introduction</h2>

This tool is very useful for the  management zabbix.
It current supports the following:
> * Templates 
> * Hostgroups
> * hosts

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

<h2 name="2">2 version</h2>
----
* v1.0.3，2016-06-11 add history_report
* v1.0.2，2016-06-03 Modify the command line in interactive mode
* v1.0.1，2016-04-16 First edit
