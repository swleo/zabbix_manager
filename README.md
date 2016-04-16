# zabbix_manager
This tool is very useful for the  management zabbix.

It current supports the following:
* Templates 
* Hostgroups
* hosts

### Usage
#### Configure zabbix_manager
First you should configure zabbix_config.ini to works with appropriate zabbix server and use right credentials.
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.118
port = 9999
user = admin
password = zabbix
``` 
#### run the main.py
Just run: 
```bash
#list the hosts
$ python main.py

```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_get.png)
#### run the main.py
Just run: 
```bash
#add a host
$ python main.py

```
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/host_add.png)
