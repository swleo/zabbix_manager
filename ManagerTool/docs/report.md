# report


<h2 name="1.4">1.4 report报表</h2>

<h3>1.4.1 简单了解内容</h3>

report 包括以下内容

服务器可用性报表
    
+ 服务器可用性报表使用Agent ping计算，Agent ping 成功时会入库1，如果失败时，则不入库。
+ trend会每个小时将history中的值计算出最大值，最小值，和平均值，这里我们需要的是trend小时的记录个数即可

服务器日常使用报表

+ CPU在一段时间内的最高值、平均值、最小值等
+ item支持模糊搜索
+ 文件系统的使用情况等

<h3>1.4.2 服务器可用性报表</h3>

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_xls.jpg)

<h3>1.4.2 服务器日常使用报表</h3>

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_table.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，

同时加--title可以输出logo旁边的title name如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_xls.jpg)
