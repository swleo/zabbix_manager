#########################################################################
# File Name: test_history_get.sh
# Author: Bill
# mail: XXXXXXX@qq.com
# Created Time: 2016-06-10 12:11:48
#########################################################################
#!/bin/bash
##报告的初始时间和结束时间（前一天的0点到24点）
from=`date  "+%Y-%m-%d 00:00:00" -d"-2day"`
now=`date  "+%Y-%m-%d 00:00:00"`

from=`date -d "$from" '+%s'`
now=`date -d "$now" '+%s'`

cd ..
python zabbix_api.py --history_get 0 23685 ${from} ${now}
python zabbix_api.py --history_get 3 23678 ${from} ${now}
