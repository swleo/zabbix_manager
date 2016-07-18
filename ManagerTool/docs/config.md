# agent自动加入监控
<h2 name="1.3">1 zabbix自动发现配置</h2>

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

自动发现规则是zabbix server去扫描一个网段，把在线的主机添加到Host列表中。适合内网下

直接执行在本目录执行 

```bash
sh scripts/config/config.sh
```
直接执行程序后，会执行操作如下

(1)创建自动发现规则

(2)自动创建action，根据action，自动将discovery的机器加到特定的主机群组中，同时链接上linux模板

<h2>2 zabbix客户端自动注册</h2>
这次是Active agent主动联系zabbix server，最后由zabbix server将这些agent加到host里。对于需要部署特别多服务器的人来说，这功能相当给力。

(1)agent

修改agent配置文件
```
ServerActive=66.175.222.222
Hostname=auto-reg-test01
HostMetadataItem=system.uname
```
(2)server

步骤：configuration>>actions>>Event source（选择Auto registration）>>CreaAction

* Action选项卡-----------定义Action名称：Action_for_autoreg
* Conditions选项卡------添加:Host metadata like Linux
* Operations选项卡-----添加:Add host,Add to host group ,Link to template
