## report报表

## 1 简单了解内容

report 包括以下内容

服务器可用性报表
    
+ 服务器可用性报表使用Agent ping计算，Agent ping 成功时会入库1，如果失败时，则不入库。
+ trend会每个小时将history中的值计算出最大值，最小值，和平均值，这里我们需要的是trend小时的记录个数即可

服务器日常使用报表

+ CPU在一段时间内的最高值、平均值、最小值等
+ item支持模糊搜索
+ 文件系统的使用情况等
+ 支持选择特定主机组或者主机

## 2 报表

### 2.1 服务器可用性报表1

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_xls.jpg)

### 2.2 服务器可用性报表2

```
#python zabbix_api.py  --report_available2 "2016-07-01 00:00:00" "2016-09-01 00:00:00" --hostid 10105 --table
```
程序输出

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table2.jpg)

zabbix界面上显示

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table3.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，如下

### 2.3 服务器日常使用报表 

```
直接输出
#python zabbix_api.py --report item_name date_from date_till

以表格形式展示在终端输出
#python zabbix_api.py --report item_name date_from date_till --table

以表格形式展示在终端输出,同时将第六列升序输出
#python zabbix_api.py --report item_name date_from date_till --table --sort 6

以表格形式展示在终端输出,同时将第六列降序输出
#python zabbix_api.py --report item_name date_from date_till --table --sort 6 --desc
```

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_table.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，

同时加--title可以输出logo旁边的title name如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_xls.jpg)

## 3 内部算法

### 3.1 服务器可用性报表1

可用性

> * 分子是：每小时统计个数的总和
> * 分母是：每小时应该统计的个数 * 小时数

每小时的个数 = 3600(小时总秒数)/X(每X秒采集一次数据)

X为item的delay值

### 3.2 服务器可用性报表2

可用性

> * 分子是：触发器判断后正常的时间段
> * 分母是：统计的时间段值

当触发器判断正常时，在event中记录的value值为0，反之，记录的值为1

根据统计1———>0状态的总时间  与  统计的时间段相比，就可以得出服务器的可用性

在程序设计时有以下几种情况，event表中存放的是0101010101值，每个值都记录着发生的时间
 
> * 取值time_from时，此item在此阶段还没有值，即还未开始监控此节点的服务，即获取到的值为0101010....，***此情况需要将分母中统计的时间段的开始值time_from设置为检查为0的时间点值***
> * 取值time_from时，此item在此阶段后，检测到有异常，即获取到的值为10101010.......
> * 取值time_till时，此item在time_till时是正常状态,即获取到的值为....101010
> * 取值time_till时，此item在time_till时是异常状态,即获取到的值为....1010101***此情况需要将最后检测为1的时间点到time_till之间的值加入到分子中***

在程序中重点需要处理，第一个值为0或者1，和最后一个值是0或者1的部分，中间部分都是使用0的时间点减去1的时间点的值

## 4 提示

(1)不加条件项时默认输出所有主机信息，如果有特定选择可以选择以下方式

```
--hostgroupid "主机组ID1，主机组ID2..."
--hostid "主机ID1，主机ID2..."
```
