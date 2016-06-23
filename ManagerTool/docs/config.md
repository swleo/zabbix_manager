# configure rule


[返回主页](https://github.com/BillWang139967/zabbix_manager/tree/master/ManagerTool)


<h2 name="1.3">1.3 配置rule</h2>

<h3>(1)修改配置文件zabbix_config.ini</h3>

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

然后修改scripts/config/config.sh程序

```bash
#!/bin/bash

info_echo(){
    echo -e "\033[42;37m[Info]: $1 \033[0m"
}

info_echo "create rule"
python ./lib_zabbix/zabbix_api.py  --drule_add "agent discovery" "192.168.199.1-252"
info_echo "create action_discovery"
python ./lib_zabbix/zabbix_api.py  --action_discovery_add "Auto discovery" store
``` 
<h3>(2)创建自动发现规则</h3>
直接执行在本目录执行 

```bash
sh scripts/config/config.sh
```
直接执行程序后，会执行操作如下

(1)创建自动发现规则

(2)自动创建action，根据action，自动将discovery的机器加到特定的主机群组中，同时链接上linux模板

