#!/usr/bin/python 
#coding:utf-8 
__version__ = "1.1.3"
 
import json 
import urllib2 
from urllib2 import URLError 
import ConfigParser
import sys
import os
import time
import unicodedata
import config

root_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root_path, 'w_lib'))

from colorclass import Color
from terminaltables import SingleTable
import my_sort
import my_compare
import XLSWriter
from BLog import Log
import argparse
reload(sys)
sys.setdefaultencoding("utf-8")
def err_msg(msg):
    print "\033[41;37m[Error]: %s \033[0m"%msg
    exit()

  
def info_msg(msg):
    print "\033[42;37m[Info]: %s \033[0m"%msg

  
def warn_msg(msg):
    print "\033[43;37m[Warning]: %s \033[0m"%msg

class zabbix_api: 
    def __init__(self,terminal_table,debug=False,output=True,output_sort=False,sort_reverse=False): 
        if os.path.exists("zabbix_config.ini"):
            config = ConfigParser.ConfigParser()
            config.read("zabbix_config.ini")
            # 是否输出显示
            self.output = output
            # 输出结果第几列排序
            self.output_sort = int(output_sort)
            self.reverse = sort_reverse
            self.server = config.get("zabbixserver", "server")
            self.port = config.get("zabbixserver", "port")
            self.user = config.get("zabbixserver", "user")
            self.password = config.get("zabbixserver", "password")
        else:
            print "the config file is not exist"
            exit(1)

        self.url = 'http://%s:%s/api_jsonrpc.php' % (self.server,self.port) #修改URL
        self.header = {"Content-Type":"application/json"}
        self.terminal_table=terminal_table
        self.authID = self.user_login() 
        logpath = "/tmp/zabbix_tool.log"
        self.logger = Log(logpath,level="debug",is_console=debug, mbs=5, count=5)

    def user_login(self): 
        data = json.dumps({
                           "jsonrpc": "2.0",
                           "method": "user.login",
                           "params": { 
                                      "user": self.user, #修改用户名
                                      "password": self.password #修改密码
                                      },
                           "id": 0 
                           })
         
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
     
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "\033[041m 用户认证失败，请检查 !\033[0m", e
            exit(1)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            self.authID = response['result'] 
            return self.authID 
         
    ##
    # @brief host_get 
    # @param hostName
    #
    # @return 
    def host_get(self,hostName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                          "output": "extend",
                          "filter":{"host":hostName} 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "主机数量: \033[31m%s\033[0m"%(len(response['result']))
            if self.terminal_table:
                table_show=[]
                table_show.append(["HostID","HostName","name","Status","Available"])
            else:
                print "HostID","HostName","name","Status","Available"

            if len(response['result']) == 0:
                return 0
            for host in response['result']:      
                status={"0":"OK","1":"Disabled"}
                available={"0":"Unknown","1":Color('{autobggreen}available{/autobggreen}'),"2":Color('{autobgred}Unavailable{/autobgred}')}
                if len(hostName)==0:
                    #print host
                    if self.terminal_table:
                        table_show.append([host['hostid'],host['host'],host['name'],status[host['status']],available[host['available']]])
                    else:
                        print host['hostid'],host['host'],host['name'],status[host['status']],available[host['available']]
                else:
                    print host['hostid'],host['host'],host['name'],status[host['status']],available[host['available']]
                    return host['hostid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)

    #  (1)Return all hosts.
    #  (2)Return only hosts that belong to the given groups.
    #  (3)Return only hosts with the given host IDs.
    def _host_get(self,hostgroupID='',hostID=''): 
        all_host_list=[]
        if hostgroupID:
            group_list=[]
            group_list[:]=[]
            for i in hostgroupID.split(','):
                group_list.append(i)
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                              "groupids":group_list,
                              "output": "extend",
                              },
                    "auth": self.user_login(),
                    "id": 1
                    })
        elif hostID:
            host_list=[]
            host_list[:]=[]
            for i in hostID.split(','):
                host_list.append(i)
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                              "hostids":host_list,
                              "output": "extend",
                              },
                    "auth": self.user_login(),
                    "id": 1
                    })
        else:
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                              "output": "extend",
                              },
                    "auth": self.user_login(),
                    "id": 1
                    })

        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return []
            for host in response['result']:      
                all_host_list.append((host['hostid'],host['host'],host['name']))
            return all_host_list

    def host_create(self, hostip,hostname,hostgroupName, templateName): 
        if self.host_get(hostname):
            print "\033[041m该主机已经添加!\033[0m" 
            sys.exit(1)

        group_list=[]
        template_list=[]
        for i in hostgroupName.split(','):
            var = {}
            var['groupid'] = self.hostgroup_get(i)
            group_list.append(var)
        for i in templateName.split(','):
            var={}
            var['templateid']=self.template_get(i)
            template_list.append(var)   

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"host.create", 
                           "params":{ 
                                     "host": hostname, 
                                     "interfaces": [ 
                                     { 
                                     "type": 1, 
                                     "main": 1, 
                                     "useip": 1, 
                                     "ip": hostip, 
                                     "dns": "", 
                                     "port": "10050" 
                                      } 
                                     ], 
                                   "groups": group_list,
                                   "templates": template_list,
                                     }, 
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            print response
            result.close() 
            print "添加主机 : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (hostip, response['result']['hostids']) 


    def host_disable(self,hostname):
        data=json.dumps({
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
            "hostid": self.host_get(hostname),
            "status": 1
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key, self.header[key])       
        try: 
            result = urllib2.urlopen(request)
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close()
            print '----主机现在状态------------'
        print self.host_get(hostname)
                 
    def host_delete(self,hostnames):
        hostid_list=[]
        #print type(hostid)
        for i in hostnames.split(','):
            hostid = self.host_get(i)
            hostid_list.append(hostid)      
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "host.delete",
                "params": hostid_list,
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
             
        try: 
            result = urllib2.urlopen(request) 
        except Exception,e: 
            print  e
        else: 
            response = json.loads(result.read()) 
            #print response['result']

            result.close() 
            print "主机 \033[041m %s\033[0m  已经删除 !"%hostnames
    # hostgroup
    def hostgroup_get(self, hostgroupName=''): 
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"hostgroup.get", 
                           "params":{ 
                                     "output": "extend", 
                                     "filter": { 
                                                "name": hostgroupName 
                                                } 
                                     }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            for group in response['result']:
                if  len(hostgroupName)==0:
                    print "hostgroup:  \033[31m%s\033[0m \tgroupid : %s" %(group['name'],group['groupid'])
            else:
                #print "hostgroup:  \033[31m%s\033[0m\tgroupid : %s" %(group['name'],group['groupid'])
                self.hostgroupID = group['groupid'] 
                return group['groupid'] 

    def _hostgroup_get_name(self, groupid=''): 
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"hostgroup.get", 
                           "params":{ 
                                     "output": "extend", 
                                     "filter": { 
                                                "groupid": groupid
                                                } 
                                     }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            for group in response['result']:
                if  len(groupid)==0:
                    print "hostgroup:  \033[31m%s\033[0m \tgroupid : %s" %(group['name'],group['groupid'])
            else:
                #print "hostgroup:  \033[31m%s\033[0m\tgroupid : %s" %(group['name'],group['groupid'])
                return group['name'] 

    def hostgroup_create(self,hostgroupName):

        if self.hostgroup_get(hostgroupName):
            print "hostgroup  \033[42m%s\033[0m is exist !"%hostgroupName
            sys.exit(1)
        data = json.dumps({
                          "jsonrpc": "2.0",
                          "method": "hostgroup.create",
                          "params": {
                          "name": hostgroupName
                          },
                          "auth": self.user_login(),
                          "id": 1
                          })
        request=urllib2.Request(self.url,data)

        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request)
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close()
            print "\033[042m 添加主机组:%s\033[0m  hostgroupID : %s"%(hostgroupName,response['result']['groupids'])


    # item
    ##
    # @brief item_get 
    #
    # @param host_ID
    # @param itemName
    #
    # @return list
    # list_format
    # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']]
    def item_get(self, host_ID='',itemName='',show=True): 
        if  len(host_ID)==0:
            print "ERR- host_ID is null"
            return 0

        table_show=[]
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"item.get", 
                           "params":{ 
                                     "output":"extend",
                                     "hostids":host_ID,
                                     }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        #dd"filter":{"name":itemName} 
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            table_show.append(["itemid","name","key_","update_time","value_type"])
            if len(response['result']) == 0:
                return 0
            item_list=[]
            item_list[:]=[]
            for item in response['result']:
                #########################################
                # alt the $1 and $2 
                #########################################
                position = item['key_'].find('[')+1
                if position:
                    list_para = item['key_'][position:-1].split(",")
                    # 将$1,$2等置换为真正name
                    for para_a in range(len(list_para)):
                        para='$'+str(para_a+1)
                        item['name']=item['name'].replace(para,list_para[para_a])

                if  len(itemName)==0:
                    table_show.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']])
                    item_list.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
                else:
                    if item['name']==itemName:
                        item_list.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
                    else:
                        if my_compare.my_compare(item['name'],itemName):
                            item_list.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
            
            if (len(itemName) == 0) and show:
                table=SingleTable(table_show)
                print(table.table)
            if len(item_list):
                return item_list
            else:
                return 0

    ##
    # @param item_ID
    # @return list
    # list_format
    # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']]

    def _item_search(self,item_ID=''): 
        table_show=[]
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"item.get", 
                           "params":{ 
                                     "output":"extend",
                                     "itemids":item_ID,
                                     }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            table_show.append(["itemid","name","key_","update_time","value_type"])
            if len(response['result']) == 0:
                return 0
            return response['result'][0]['value_type']
    # history
    def history(self,item_ID='',date_from='',date_till=''): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")
        time_from = int(time.mktime(startTime))
        time_till = int(time.mktime(endTime))
        history_type=self._item_search(item_ID)
        self._history_get(history_type,item_ID,time_from,time_till)
            
    def _history_get(self,history='',item_ID='',time_from='',time_till=''): 
        history_data=[]
        history_data[:]=[]
              
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"history.get", 
                           "params":{ 
                                     "time_from":time_from,
                                     "time_till":time_till,
                                     "output": "extend",
                                     "history": history,
                                     "itemids": item_ID,
                                     "sortfield":"clock",
                                     "limit": 10080
                                     }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                warn_msg("not have history_data")
                debug_info=str([history,item_ID,time_from,time_till,"####not have history_data"])
                self.logger.debug(debug_info)
                return 0.0
            for history_info in response['result']:
                print item_ID,history_info['value']
            
    ##
    # @return 
    def _get_select_condition_info(self,select_condition): 
        output = ""
        if select_condition["hostgroupID"]:
            flag = 1
            for i in select_condition["hostgroupID"].split(','):
                hostgroup_name = self._hostgroup_get_name(i)
                #print hostgroup_name
                if flag:
                    flag = 0
                    output = hostgroup_name + output
                else:
                    output = hostgroup_name+u"、"+output
            output = u"主机组:" + output 
        else:
            output = u"主机组:" + u"无"
        if select_condition["hostID"]:
            flag = 1
            host_name = self._host_get(hostID=select_condition["hostID"])
            for host_info in host_name:
                if flag:
                    output = host_info[2]+"\n"+output
                else:
                    output = host_info[2]+u"、"+output
            output = u"主机:" + output 
        else:
            output = u"主机:" + u"无" + "\n" + output
        return output
    ##
    # @brief report 
    #
    # @param itemName
    # @param date_from
    # @param date_till
    # @param export_xls 
    #
    # @return 
    def report(self,itemName,date_from,date_till,export_xls,select_condition): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            err_msg("date_till must after the date_from time")


        # 获取需要输出报表信息的host_list
        if select_condition["hostgroupID"] or select_condition["hostID"]:
            xls_range = self._get_select_condition_info(select_condition)
                
            host_list_g=[]
            host_list_h=[]
            if select_condition["hostgroupID"]:
                host_list_g=self._host_get(hostgroupID=select_condition["hostgroupID"])
            if select_condition["hostID"]:
                host_list_h=self._host_get(hostID=select_condition["hostID"])
            # 将host_list_h的全部元素添加到host_list_g的尾部
            host_list_g.extend(host_list_h)

            # 去除列表中重复的元素
            host_list = list(set(host_list_g))
        else:
            xls_range = u"ALL"
            host_list = self._host_get()
        for host_info in host_list: 
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                continue
            for itemid_sub_list in itemid_all_list:
                itemid = itemid_sub_list[0]
                item_name = itemid_sub_list[1]
                item_key = itemid_sub_list[2]
                history_type = itemid_sub_list[4]
                debug_msg="itemid:%s"%itemid
                self.logger.debug(debug_msg)
                report_min,report_max,report_avg = self.trend_get(itemid,time_from,time_till)
                if history_type=="3":
                    report_min=int(report_min)
                    report_max=int(report_max)
                    report_avg=int(report_avg)
                report_min=str(report_min)
                report_max=str(report_max)
                report_avg=str(report_avg)
                itemid=str(itemid)
                report_output.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            reverse = self.reverse
            if self.output_sort in [4,5,6]:
                if history_type=="3":
                    report_output = sorted(report_output,key=lambda x:int(x[self.output_sort-1]),reverse=reverse)
                else:
                    report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1]),reverse=reverse)
            if self.output_sort in [1]:
                report_output = sorted(report_output,key=lambda x:int(x[self.output_sort-1]),reverse=reverse)
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append(["hostid","name","itemName","min","max","avg"])
            for report_item in report_output:
                table_show.append(report_item)
            table=SingleTable(table_show)
            table.title = itemName
            print(table.table)
        else:
            print "hostid",'\t',"name",'\t',"itemName",'\t',"min",'\t',"max","avg"
            for report_item in report_output:
                for report_item_i in report_item:
                    print report_item_i,'\t',
                print 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    def agent_ping(self,item_ID='',time_from='',time_till=''): 
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trend.get", 
                           "params":{ 
                               "time_from":time_from,
                               "time_till":time_till,
                               "output":[
                                   "itemid",
                                   "clock",
                                   "num",
                                   "value_min",
                                   "value_avg",
                                   "value_max"
                                        ],
                               "itemids":item_ID,
                               "limit":"8760"
                                     }, 

                           "auth":self.user_login(), 
                           "id":1, 
                           }) 

        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            #print response
            result.close() 
            if len(response['result']) == 0:
                debug_info=str([item_ID,time_from,time_till,"####not have trend_data"])
                self.logger.debug(debug_info)
                return 0,0,0
            sum_num_value = 0
            sum_avg_value = 0
            for result_info in response['result']:
                hour_num_string = unicodedata.normalize('NFKD',result_info['num']).encode('ascii','ignore')
                hour_num=eval(hour_num_string)
                sum_num_value = sum_num_value + hour_num
                
                hour_avg_string = unicodedata.normalize('NFKD',result_info['value_avg']).encode('ascii','ignore')
                hour_avg=eval(hour_avg_string)
                sum_avg_value = sum_avg_value + hour_avg
            trend_sum = len(response['result'])
            return trend_sum,sum_num_value,sum_avg_value

    def _diff_hour(self,date1,date2):
        diff_seconds = date2 - date1
        diff_hour = diff_seconds / 3600
        return diff_hour
    ##
    # @brief report_available
    #
    # @param itemName
    # @param date_from
    # @param date_till
    # @param export_xls
    #
    # @return 
    def report_available(self,itemName,date_from,date_till,export_xls,select_condition,value_type=False): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        if export_xls["xls"] == 'ON':
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            if export_xls["title"] == 'ON':
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))-1
        diff_hour = self._diff_hour(time_from,time_till)

        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        if self.terminal_table:
            table_show=[]
            table_show.append([u"hostid",u"资源类型",u"itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"])
        else:
            print "hostid",'\t',u"资源类型",'\t',"itemName",'\t',u"期望值(%)",'\t',u"平均值(%)",'\t',u"差值(%)"
        # 获取需要输出报表信息的host_list
        if select_condition["hostgroupID"] or select_condition["hostID"]:
            if export_xls["xls"] == 'ON':
                output_info = self._get_select_condition_info(select_condition)
                xlswriter.add_remark(u"范围:"+output_info,6,sheet_name=sheetName)
                xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern_n=22)
            host_list_g=[]
            host_list_h=[]
            if select_condition["hostgroupID"]:
                host_list_g=self._host_get(hostgroupID=select_condition["hostgroupID"])
            if select_condition["hostID"]:
                host_list_h=self._host_get(hostID=select_condition["hostID"])
            # 将host_list_h的全部元素添加到host_list_g的尾部
            host_list_g.extend(host_list_h)

            # 去除列表中重复的元素
            host_list = list(set(host_list_g))
        else:
            if export_xls["xls"] == 'ON':
                output_info = u"ALL"
                xlswriter.add_remark(u"范围:"+output_info,6,sheet_name=sheetName)
                xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern_n=22)
            host_list = self._host_get()
        for host_info in host_list: 
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                continue
            for itemid_sub_list in itemid_all_list:
                itemid=itemid_sub_list[0]
                item_name=itemid_sub_list[1]
                item_key=itemid_sub_list[2]
                item_update_time=itemid_sub_list[3]
                
                check_time=int(item_update_time)
                if not check_time:
                    check_time = 60
                hour_check_num = int(3600/check_time)
                trend_sum,sum_num_value,sum_avg_value = self.agent_ping(itemid,time_from,time_till)
                
                if (sum_avg_value > 0) and (trend_sum > 0):
                    # 分子为trend_avg平均值之和
                    sum_avg_value_p = float(sum_avg_value*100)
                    sum_check=trend_sum*hour_check_num

                    # 默认0不入库，分母为时间小时差
                    sum_value = diff_hour
                    value_type_info = "null"
                    # 如果0入库，分母为获取到的thrend数
                    if value_type:
                        sum_value = trend_sum
                        value_type_info = "zero"

                    avg_ping=sum_avg_value_p/sum_value

                                

                    if avg_ping == 100:
                        avg_ping =int(avg_ping)
                    else:
                        avg_ping=float('%0.2f'% avg_ping)
                    diff_ping = avg_ping - 100
                else:
                    avg_ping = 0
                    diff_ping = 0
                    sum_check = -1
                    value_type_info = "-1"
                
                debug_msg="time[%s] hour[%s] itemid:%s update_time:%s trend_sum:%d,sum_avg:%s,sum_num:%d,expected_value:%s type:%s"\
                        %(str(sheetName),str(diff_hour),itemid,item_update_time,trend_sum,str(sum_avg_value),sum_num_value,str(sum_check),value_type_info)
                self.logger.debug(debug_msg)

                if self.terminal_table:
                    table_show.append([host_info[0],host_info[2],item_name,"100",str(avg_ping),str(diff_ping)])
                else:
                    print host_info[0],'\t',host_info[2],'\t',item_name,'\t',"100",'\t',avg_ping,'\t',diff_ping
                if export_xls["xls"] == "ON":
                    xlswriter.writerow([host_info[0],host_info[2],item_name,"100",str(avg_ping),str(diff_ping)],sheet_name=sheetName,border=True)
        print
        if self.terminal_table:
            table=SingleTable(table_show)
            table.title = itemName
            print(table.table)
        if export_xls["xls"] == 'ON':
            xlswriter.save()
        return 0
    ##
    # @return 
    def report_available2(self,date_from,date_till,export_xls,select_condition,value_type=False): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))-1
        diff_hour = self._diff_hour(time_from,time_till)

        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        # 获取需要输出报表信息的host_list
        if select_condition["hostgroupID"] or select_condition["hostID"]:
            xls_range = self._get_select_condition_info(select_condition)
                
            host_list_g=[]
            host_list_h=[]
            if select_condition["hostgroupID"]:
                host_list_g=self._host_get(hostgroupID=select_condition["hostgroupID"])
            if select_condition["hostID"]:
                host_list_h=self._host_get(hostID=select_condition["hostID"])
            # 将host_list_h的全部元素添加到host_list_g的尾部
            host_list_g.extend(host_list_h)

            # 去除列表中重复的元素
            host_list = list(set(host_list_g))
        else:
            xls_range = u"ALL"
            host_list = self._host_get()
        for host_info in host_list: 
            #print "####",host_info[0]
            triggerid_all_list = self.triggers_get(host_info[0])
            if triggerid_all_list == 0:
                continue
            #print time_from,time_till
            for triggerid_sub_list in triggerid_all_list:
                triggerid=triggerid_sub_list[0]
                trigger_name=triggerid_sub_list[1]
                event_result = self.event_get(triggerid,time_from,time_till,value="1")
                if not event_result:
                    report_output.append([trigger_name,"0","100%"])
                else:
                    event_result = self.event_get(triggerid,time_from,time_till)
                    if not event_result:
                        report_output.append([trigger_name,"0","100%"])
                    else:
                        event_result = float(event_result)
                        event_diff = "%0.4f%%"%event_result
                        event_value = "%0.4f%%"%(100.0 - event_result)
                        report_output.append([trigger_name,event_diff,event_value])
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append(["Name","Problems","OK"])
            for report_item in report_output:
                table_show.append(report_item)
            table=SingleTable(table_show)
            table.title = "Availability report"
            print(table.table)
        else:
            print "Name",'\t',"Problems",'\t',"OK"
            for report_item in report_output:
                for report_item_i in report_item:
                    print report_item_i,'\t',
                print 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_image("python.bmg",0,0,3,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,3,sheet_name=sheetName)
            xlswriter.setcol_width([50,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,3,sheet_name=sheetName)
            xlswriter.writerow(["name","Problems","OK"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    ##
    # @return 
    def report_flow(self,date_from,date_till,export_xls,hosts_file="./switch"): 
        host_all_info = config.read_config(hosts_file)
        #print host_all_info
        dateFormat = "%Y-%m-%d %H:%M:%S"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        if export_xls["xls"] == 'ON':
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            if export_xls["title"] == 'ON':
                xlswriter.add_image2("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image2("python.bmg",0,0,sheet_name=sheetName)
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([5,58,20,20,8,8,8,8,8,8,8,8,8,8,8,8,8,11],sheet_name=sheetName)
            xlswriter.write_title(sheet_name=sheetName,border=True,pattern_n=22)

        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        print \
            "nu",\
            "description",\
            "hostname|",\
            "ethernet_port|",\
            "speed",\
            "in_max|",\
            "in_avg|",\
            "in_min|",\
            "rate_in_max|",\
            'rate_in_avg|',\
            "rate_in_min|",\
            "out_max|",\
            "out_avg|",\
            "out_min",\
            "rate_out_max|",\
            "rate_out_avg|",\
            "rate_out_min|",\
            "bandwidth"
        # 获取需要输出报表信息的host_list
        num=1
        for host_info in host_all_info: 
            # host_info (description,hostid,ethernet_port,default_speed)
            description = host_info[0]
            hostid = host_info[1]
            host_name_list = self._host_get(hostID=hostid)
            if len(host_name_list) == 0:
                continue
            host_name=host_name_list[0][2]
            ethernet_port = host_info[2]
            default_speed = host_info[3]
            
            item_ethernet_port_in = "Incoming network traffic on " + ethernet_port
            item_ethernet_port_out = "Outgoing network traffic on " + ethernet_port

            # speed
            speed_flag=False
            if default_speed != "AUTO":
                speed = float(default_speed)
            else:
                item_speed = "Speed on " + ethernet_port
                itemid_all_list = self.item_get(hostid,item_speed)
                if itemid_all_list:
                    itemid=itemid_all_list[0][0]
                    report_min,report_max,report_avg = self.trend_get(itemid,time_from,time_till)
                    speed = report_max
                    if speed == 0:
                        speed = 1000
                        speed_flag = True
                else:
                    speed = -1
                
            # ethernet_port
            itemid_in_list = self.item_get(hostid,item_ethernet_port_in)
            if itemid_in_list:
                itemid_in=itemid_in_list[0][0]
                in_min,in_max,in_avg = self.trend_get(itemid_in,time_from,time_till)
                in_min = float('%0.4f'%(in_min /1000000.0))
                in_max = float('%0.4f'%(in_max /1000000.0))
                in_avg = float('%0.4f'%(in_avg /1000000.0))
            #print in_max,in_avg,in_min
                rate_in_min = float('%0.4f'% (in_min/speed * 100))
                rate_in_max = float('%0.4f'% (in_max/speed * 100))
                rate_in_avg = float('%0.4f'% (in_avg/speed * 100))
            else:
                print "no item[%s]"%item_ethernet_port_in
                in_min = -1
                in_max = -1
                in_avg = -1
                rate_in_min = -1
                rate_in_max = -1
                rate_in_avg = -1


            itemid_out_list = self.item_get(hostid,item_ethernet_port_out)
            if itemid_out_list:
                itemid_out = itemid_out_list[0][0]
                out_min,out_max,out_avg = self.trend_get(itemid_out,time_from,time_till)
                out_min = float('%0.4f'%(out_min /1000000.0))
                out_max = float('%0.4f'%(out_max /1000000.0))
                out_avg = float('%0.4f'%(out_avg /1000000.0))
                rate_out_min = float('%0.4f'%(out_min/speed * 100))
                rate_out_max = float('%0.4f'%(out_max/speed * 100))
                rate_out_avg = float('%0.4f'%(out_avg/speed * 100))
            else:
                print "no item[%s]"%item_ethernet_port_out
                out_min = -1
                out_max = -1
                out_avg = -1
                rate_out_min = -1
                rate_out_max = -1
                rate_out_avg = -1

            if rate_in_max > rate_out_max:
                bandwidth = rate_in_max
            else:
                bandwidth =rate_out_max

            print \
                num,\
                description,\
                host_name,\
                ethernet_port,\
                speed,\
                in_max,\
                in_avg,\
                in_min,\
                rate_in_max,\
                rate_in_avg,\
                rate_in_min,\
                out_max,\
                out_avg,\
                out_min,\
                rate_out_max,\
                rate_out_avg,\
                rate_out_min,\
                bandwidth
            if export_xls["xls"] == "ON":
                if speed_flag:
                    xlswriter.writerow([
                        num,\
                        description,\
                        host_name,\
                        ethernet_port,\
                        speed,\
                        in_max,\
                        in_avg,\
                        in_min,\
                        rate_in_max,\
                        rate_in_avg,\
                        rate_in_min,\
                        out_max,\
                        out_avg,\
                        out_min,\
                        rate_out_max,\
                        rate_out_avg,\
                        rate_out_min,\
                        bandwidth],
                        sheet_name=sheetName,border=True,pattern_n=2)
                else:
                    xlswriter.writerow([
                        num,\
                        description,\
                        host_name,\
                        ethernet_port,\
                        speed,\
                        in_max,\
                        in_avg,\
                        in_min,\
                        rate_in_max,\
                        rate_in_avg,\
                        rate_in_min,\
                        out_max,\
                        out_avg,\
                        out_min,\
                        rate_out_max,\
                        rate_out_avg,\
                        rate_out_min,\
                        bandwidth],
                        sheet_name=sheetName,border=True)
                num=num+1
                    
        print
        if self.terminal_table:
            table=SingleTable(table_show)
            table.title = itemName
            print(table.table)
        if export_xls["xls"] == 'ON':
            xlswriter.save()
        return 0
    def alert_get(self):
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "alert.get",
                "params": {
                    "output":"extend",
                    "actionids":"3"
                },
                "auth": self.user_login(),
                "id": 1
                })
        print data
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
             
        try: 
            result = urllib2.urlopen(request) 
        except Exception,e: 
            print  e
        else: 
            response = json.loads(result.read()) 
            #print response['result']
            print response
            result.close() 
    ##
    # @brief trend_get 
    #
    # @param itemID
    #
    # @return itemid
    def trend_get(self,itemID='',time_from='',time_till=''): 
        trend_min_data=[]
        trend_max_data=[]
        trend_avg_data=[]
        trend_min_data[:]=[]
        trend_max_data[:]=[]
        trend_avg_data[:]=[]
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trend.get", 
                           "params":{ 
                               "time_from":time_from,
                               "time_till":time_till,
                               "output":[
                                   "itemid",
                                   "clock",
                                   "num",
                                   "value_min",
                                   "value_avg",
                                   "value_max"
                                        ],
                               "itemids":itemID,
                               "limit":"8760"
                                     }, 

                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                debug_info=str([itemID,time_from,time_till,"####not have trend_data"])
                self.logger.debug(debug_info)
                return 0.0,0.0,0.0
            for result_info in response['result']:
                trend_min_data.append(result_info['value_min'])
                    
                trend_max_data.append(result_info['value_max'])
                trend_avg_data.append(result_info['value_avg'])
            trend_min_data_all=my_sort.Stats(trend_min_data)
            trend_max_data_all=my_sort.Stats(trend_max_data)
            trend_avg_data_all=my_sort.Stats(trend_avg_data)
            trend_min=trend_min_data_all.min()
            trend_max=trend_max_data_all.max()
            trend_avg=float('%0.4f'% trend_avg_data_all.avg())
            
            return (trend_min,trend_max,trend_avg)
    # template
    def template_get(self,templateName=''): 
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method": "template.get", 
                           "params": { 
                                      "output": "extend", 
                                      "filter": { 
                                                 "name":templateName                                                        
                                                 } 
                                      }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           })
         
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            if self.terminal_table:
                table_show=[]
                table_show.append(["template","id"])
            result.close() 
            for template in response['result']:                
                if len(templateName)==0:
                    if self.terminal_table:
                        table_show.append([template['name'],template['templateid']])
                    else:
                        print "template : \033[31m%s\033[0m\t  id : %s" % (template['name'], template['templateid'])
                else:
                    self.templateID = response['result'][0]['templateid'] 
                    #print "Template Name :  \033[31m%s\033[0m "%templateName
                    return response['result'][0]['templateid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    def configuration_import(self,template): 
        rules = {
            'applications': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'discoveryRules': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'graphs': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'groups': {
                'createMissing': 'true'
            },
            'hosts': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'images': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'items': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'maps': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'screens': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templateLinkage': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templates': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templateScreens': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'triggers': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
        }

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method": "configuration.import", 
                           "params": { 
                                      "format": "xml", 
                                      "rules": rules,
                                      "source":template
                                      }, 
                           "auth":self.user_login(), 
                           "id":1, 
                           })
         
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print response['result']
            #print "add user : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (usergroupName, response['result']['userids'][0]) 
    # user
    ##
    # @brief user_get 
    #
    # @param userName
    #
    # @return 
    def user_get(self,userName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "user.get",
                "params": {
                          "output": "extend",
                          "filter":{"alias":userName} 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "user sum: \033[31m%s\033[0m"%(len(response['result']))
            if self.terminal_table:
                table_show=[]
                table_show.append(["userid","alias","name","url"])
            else:
                print "userid","alias","name","url"

            if len(response['result']) == 0:
                return 0
            for user in response['result']:      
                if len(userName)==0:
                    if self.terminal_table:
                        table_show.append([user['userid'],user['alias'],user['name'],user['url']])
                    else:
                        print user['userid'],user['alias'],user['name'],user['url']
                else:
                    #print user_group['usrgrpid'],user_group['name'],user_group['gui_access'],user_group['users_status']
                    return user['userid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    def user_create(self, userName,userPassword,usergroupName,mediaName,email): 
        if self.user_get(userName):
            print "\033[041mthis userName is exists\033[0m" 
            sys.exit(1)

        usergroupID=self.usergroup_get(usergroupName)
        mediatypeID=self.mediatype_get(mediaName)
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"user.create", 
                           "params": {
                                "alias": userName,
                                "passwd": userPassword,
                                "usrgrps": [
                                             {
                                             "usrgrpid": usergroupID
                                             }      
                                            ],
                                "user_medias": [
                                            {
                                                "mediatypeid": mediatypeID,
                                                "sendto": email,
                                                "active": 0,
                                                "severity": 63,
                                                "period": "1-7,00:00-24:00"
                                            }
                                                ]
                                       },
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print "add user : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (usergroupName, response['result']['userids'][0]) 
    # usergroup
    ##
    # @brief host_get 
    #
    # @param hostName
    #
    # @return 
    def usergroup_get(self,usergroupName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "usergroup.get",
                "params": {
                          "output": "extend",
                          "filter":{"name":usergroupName} 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "usergroup sum: \033[31m%s\033[0m"%(len(response['result']))

            if not len(usergroupName):
                if self.terminal_table:
                    table_show=[]
                    table_show.append(["usrgrpid","name","gui_access","users_status"])
                else:
                    print "usrgrpid","name","gui_access","users_status"

            if len(response['result']) == 0:
                return 0
            for user_group in response['result']:      
                if len(usergroupName)==0:
                    if self.terminal_table:
                        table_show.append([user_group['usrgrpid'],user_group['name'],user_group['gui_access'],user_group['users_status']])
                    else:
                        print user_group['usrgrpid'],user_group['name'],user_group['gui_access'],user_group['users_status']
                else:
                    #print user_group['usrgrpid'],user_group['name'],user_group['gui_access'],user_group['users_status']
                    return user_group['usrgrpid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    def usergroup_create(self, usergroupName,hostgroupName): 
        if self.usergroup_get(usergroupName):
            print "\033[041mthis usergroupName is exists\033[0m" 
            sys.exit(1)

        hostgroupID=self.hostgroup_get(hostgroupName)
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"usergroup.create", 
                           "params":{ 
                                     "name":usergroupName,
                                     "rights":{ 
                                         "permission": 3,
                                         "id":hostgroupID
                                      }, 
                                     }, 
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print "add usergroup : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (usergroupName, response['result']['usrgrpids'][0]) 
    def usergroup_del(self,usergroupName):
        usergroup_list=[]
        for i in usergroupName.split(','):
            usergroupID=self.usergroup_get(i)
            if usergroupID:
                usergroup_list.append(usergroupID)      
        if not len(usergroup_list):
            print "usergroup \033[041m %s\033[0m  is not exists !"% usergroupName 
            exit(1)
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "usergroup.delete",
                "params": usergroup_list,
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
             
        try: 
            result = urllib2.urlopen(request) 
        except Exception,e: 
            print  e
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "usergroup \033[042m %s\033[0m  delete OK !"% usergroupName 
    # mediatype
    ##
    # @brief mediatype_get 
    #
    # @return 
    def mediatype_get(self,mediatypeName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "mediatype.get",
                "params": {
                          "output": "extend",
                          "filter":{"description":mediatypeName} 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "mediatype sum: \033[31m%s\033[0m"%(len(response['result']))

            if not len(mediatypeName):
                if self.terminal_table:
                    table_show=[]
                    table_show.append(["mediatypeid","type","description","exec_path"])
                else:
                    print "mediatypeid","type","description","exec_path"

            if len(response['result']) == 0:
                return 0
            for mediatype in response['result']:      
                if len(mediatypeName)==0:
                    if self.terminal_table:
                        table_show.append([mediatype['mediatypeid'],mediatype['type'],mediatype['description'],mediatype['exec_path']])
                    else:
                        print mediatype['mediatypeid'],mediatype['type'],mediatype['description'],mediatype['exec_path']
                else:
                    return mediatype['mediatypeid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    # mediatypeType Possible values: 
    # 0 - email; 
    # 1 - script; 
    # 2 - SMS; 
    # 3 - Jabber; 
    def mediatype_create(self, mediatypeName,mediatypePath): 
        if self.mediatype_get(mediatypeName):
            print "\033[041mthis mediatypeName is exists\033[0m" 
            sys.exit(1)

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"mediatype.create", 
                           "params": {
                                 "description": mediatypeName,
                                 "type": 1,
                                 "exec_path": mediatypePath,
                                 "exec_params":"{ALERT.SENDTO}\n{ALERT.SUBJECT}\n{ALERT.MESSAGE}\n"
                                               },
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print "add mediatype : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (mediatypeName, response['result']['mediatypeids'][0]) 
    def mediatype_del(self,mediatypeName):
        mediatype_list=[]
        for i in mediatypeName.split(','):
            mediatypeID=self.mediatype_get(i)
            if mediatypeID:
                mediatype_list.append(mediatypeID)      
        if not len(mediatype_list):
            print "mediatype \033[041m %s\033[0m  is not exists !"% mediatypeName 
            exit(1)
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "mediatype.delete",
                "params": mediatype_list,
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
             
        try: 
            result = urllib2.urlopen(request) 
        except Exception,e: 
            print  e
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "mediatype \033[042m %s\033[0m  delete OK !"% mediatypeName 
    # drule(discoveryRules)
    def drule_get(self,druleName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "drule.get",
                "params": {
                          "output": "extend",
                          "filter":{"name":druleName} 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print "drule sum: \033[31m%s\033[0m"%(len(response['result']))
            if not len(druleName):
                if self.terminal_table:
                    table_show=[]
                    table_show.append(["druleid","name","iprange","status"])
                else:
                    print "druleid","name","iprange","status"

            if len(response['result']) == 0:
                return 0
            status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
            for drule in response['result']:      
                if len(druleName)==0:
                    if self.terminal_table:
                        table_show.append([drule['druleid'],drule['name'],drule['iprange'],status[drule['status']]])
                    else:
                        print drule['druleid'],drule['name'],drule['iprange'],status[drule['status']]
                else:
                    return drule['druleid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    def drule_create(self, druleName,iprange): 
        if self.drule_get(druleName):
            print "\033[041mthis druleName is exists\033[0m" 
            sys.exit(1)

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"drule.create", 
                           "params": {
                               "name": druleName,
                               "iprange": iprange,
                               "dchecks": [
                                           {
                                               "type": "9",
                                               "key_": "system.uname",
                                               "ports": "10050",
                                               "uniq": "0"
                                            }
                                          ]
                                      },
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            #print response
            print "add drule : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (druleName, response['result']['druleids'][0]) 
    # action
    # eventsource 0 triggers
    # eventsource 1 discovery
    # eventsource 2 auto registration
    # eventsource 3 internal
    def action_get(self,actionName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "action.get",
                "params": {
                          "output": "extend",
                          "filter":{
                              "name":actionName,
                          } 
                          },
                "auth": self.user_login(),
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print 'We failed to reach a server.' 
                print 'Reason: ', e.reason 
            elif hasattr(e, 'code'): 
                print 'The server could not fulfill the request.' 
                print 'Error code: ', e.code 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            #print "drule sum: \033[31m%s\033[0m"%(len(response['result']))
            if not len(actionName):
                if self.terminal_table:
                    table_show=[]
                    table_show.append(["actionid","name","eventsource","status"])
                else:
                    print "actionid","name","eventsource","status"

            if len(response['result']) == 0:
                return 0
            status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
            eventsource={"0":"triggers","1":"discovery","2":"registration","3":"internal"}
            for action in response['result']:      
                if len(actionName)==0:
                    if self.terminal_table:
                        table_show.append([action['actionid'],action['name'],eventsource[action['eventsource']],status[action['status']]])
                    else:
                        print action['actionid'],action['name'],eventsource[action['eventsource']],status[action['status']]
                else:
                    return action['actionid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    
    def action_autoreg_create(self, actionName,hostgroupName): 
        if self.action_get(actionName):
            output_print={}
            output_print["status"]="ERR"
            output_print["output"]="this druleName is exists"
            if self.output:
                print json.dumps(output_print)
            return json.dumps(output_print)

        hostgroupID = self.hostgroup_get(hostgroupName)
        if not hostgroupID:
            output_print={}
            output_print["status"]="ERR"
            output_print["output"]="this hostgroup is not exists"
            if self.output:
                print json.dumps(output_print)
            return json.dumps(output_print)
        templateName = "Template OS Linux"
        templateID=self.template_get(templateName)
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"action.create", 
                           "params": {
                               "name": actionName,
                               "eventsource": 2,
                               "status": 0,
                               "esc_period": 0,
                               "filter": {
                                   "evaltype": 0,
                                   "conditions": [
                                        {
                                            "conditiontype": 24,
                                            "operator": 2,
                                            "value": "Linux"
                                        }
                                   ]
                               },
                               "operations": [
                                    {
                                        "operationtype": 2,
                                        "esc_step_from": 1,
                                        "esc_period": 0,
                                        "esc_step_to": 1
                                    },
                                    {
                                        "operationtype": 4,
                                        "esc_step_from": 2,
                                        "esc_period": 0,
                                        "opgroup": [
                                            {
                                                "groupid":hostgroupID
                                            }
                                        ],
                                        "esc_step_to": 2
                                    },
                                    {
                                        "operationtype": 6,
                                        "esc_step_from": 3,
                                        "esc_period": 0,
                                        "optemplate": [
                                            {
                                                "templateid":templateID
                                            }
                                        ],
                                        "esc_step_to": 3
                                    }
                                ]
                           },
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 

            output_print={}
            output_print["status"]="OK"
            output_print["output"]="add action:%s id:%s" %(actionName, response['result']['actionids'][0]) 
            if self.output:
                print json.dumps(output_print)
            return json.dumps(output_print)
    
    def action_discovery_create(self, actionName,hostgroupName): 
        if self.action_get(actionName):
            print "\033[041mthis druleName is exists\033[0m" 
            sys.exit(1)

        hostgroupID = self.hostgroup_get(hostgroupName)
        if not hostgroupID:
            print "this hostgroup is not exists"
            exit(1)
        templateName = "Template OS Linux"
        templateID=self.template_get(templateName)
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"action.create", 
                           "params": {
                               "name": actionName,
                               "eventsource": 1,
                               "status": 0,
                               "esc_period": 0,
                               "filter": {
                                   "evaltype": 0,
                                   "conditions": [
                                        {
                                            "conditiontype": 12,
                                            "operator": 2,
                                            "value": "Linux"
                                        },
                                        {
                                            "conditiontype":10,
                                            "operator": 0,
                                            "value":"0"
                                        },
                                        {
                                            "conditiontype":8,
                                            "operator": 0,
                                            "value":"9"
                                        }
                                   ]
                               },
                               "operations": [
                                    {
                                        "operationtype": 2,
                                        "esc_step_from": 1,
                                        "esc_period": 0,
                                        "esc_step_to": 1
                                    },
                                    {
                                        "operationtype": 4,
                                        "esc_step_from": 2,
                                        "esc_period": 0,
                                        "opgroup": [
                                            {
                                                "groupid":hostgroupID
                                            }
                                        ],
                                        "esc_step_to": 2
                                    },
                                    {
                                        "operationtype": 6,
                                        "esc_step_from": 3,
                                        "esc_period": 0,
                                        "optemplate": [
                                            {
                                                "templateid":templateID
                                            }
                                        ],
                                        "esc_step_to": 3
                                    }
                                ]
                           },
                           "auth": self.user_login(), 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print "add action : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" %(actionName, response['result']['actionids'][0]) 

    def mysql_quota(self): 
        # 获取host列表
        host_list = self._host_get()
        sum_history_quota = 0
        sum_trends_quota = 0
        sum_event_quota = 0
        sum_item_num = 0
        for host_info in host_list: 
            # 获取host中的item
            itemid_all_list = self.item_get(host_info[0],show=False)
            if itemid_all_list == 0:
                continue
            itemid_num = len(itemid_all_list)
            sum_item_num = sum_item_num + itemid_num
            for itemid_sub_list in itemid_all_list:
                item_history=int(itemid_sub_list[5])
                item_update_time=int(itemid_sub_list[3])
                if not item_update_time:
                    item_update_time = 60
                history_quota = item_history * 24 * 3600 * 50 / item_update_time
                sum_history_quota = sum_history_quota + history_quota
                
        sum_trends_quota = 365 * sum_item_num * 24 * 128
        sum_event_quota = 365 * sum_item_num * 24 * 130 * 5
        mysql_quota = (sum_history_quota + sum_trends_quota + sum_event_quota)/1000000000.0
        print "item_num:%d Use:%fG"%(sum_item_num,mysql_quota)
        return 0
    
    #triggers
    def triggers_get(self, host_ID='',show=True): 
        if  len(host_ID)==0:
            print "ERR- host_ID is null"
            return 0

        all_trigger_list=[]
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trigger.get", 
                           "params":{ 
                                     "output":"extend",
                                     "hostids":host_ID,
                                     "expandData":"1",
                                     "expandDescription":"1"
                                     }, 
                               #"selectHosts":host_ID,
                           "auth":self.user_login(), 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            for trigger in response['result']:
                all_trigger_list.append((trigger["triggerid"],trigger["description"]))
            return all_trigger_list
    
    def event_get(self, triggerid='',time_from='',time_till='',value="",show=True): 
        if value:
            data = json.dumps({ 
                               "jsonrpc":"2.0", 
                               "method":"event.get", 
                               "params":{ 
                                         "output":"extend",
                                         "objectids": triggerid,
                                         "time_from":time_from,
                                         "time_till":time_till,
                                         "value":"1",
                                         }, 
                               "auth":self.user_login(), 
                               "id":1, 
                               }) 
        else:
            data = json.dumps({ 
                               "jsonrpc":"2.0", 
                               "method":"event.get", 
                               "params":{ 
                                         "output":"extend",
                                         "objectids": triggerid,
                                         "time_from":time_from,
                                         "time_till":time_till,
                                         }, 
                               "auth":self.user_login(), 
                               "id":1, 
                               }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print "Error as ", e 
        else: 
            response = json.loads(result.read()) 
            result.close() 
            # 如果输出值为0时，可用性为100%
            if len(response['result']) == 0:
                return 0
            
            # 当输出的value 包含0值时
            if not value:
                # 当输出只有1个值时，可用性为100%
                if len(response['result']) == 1:
                    return 0
                # 输出的列表第一个值为0,表示添加此监控项的时间在时间条件之间，应根据添加监控项的时间为起始时间
                if response['result'][0]["value"] == "0":
                    time_from_record = int(response['result'][0]["clock"])
                    response["result"]=response["result"][1:]
                    time_range = time_till - time_from_record
                    time_event_sum = 0
                    time_diff = 0
                    #print "debug####",len(response["result"])
                    for i in range(len(response["result"])):
                        if(i%2) == 0:
                            time_diff = int(response["result"][i+1]["clock"]) - int(response["result"][i]["clock"])
                            time_event_sum = time_event_sum + time_diff
                    event_diff = float('%0.4f'%(time_event_sum * 100 / float(time_range)))
                    #print event_diff
                    return event_diff
                else:
                    time_from_record = time_from
                    time_range = time_till - time_from_record
                    time_event_sum = 0
                    time_diff = 0
                    if len(response["result"])%2 == 1:
                           return 0
                    for i in range(len(response["result"])):
                        if(i%2) == 0:
                            time_diff = int(response["result"][i+1]["clock"]) - int(response["result"][i]["clock"])
                            time_event_sum = time_event_sum + time_diff
                    event_diff = float('%0.4f'%(time_event_sum * 100 / float(time_range)))
                    return event_diff
            else:
                # 表示包含值为1的事件
                return 1



if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='zabbix  api ',usage='%(prog)s [options]')
   
    #####################################
    parser_host = parser.add_argument_group('host')
    parser_host.add_argument('--group',nargs='?',metavar=('GroupName'),dest='listgroup',default='group',help='查询主机组')
    parser_host.add_argument('--hostgroup_add',
                        nargs=1,
                        metavar=('GroupName'),
                        dest='hostgroup_add',
                        help='添加主机组')
    parser_host.add_argument('--host',
                             nargs='?',
                             metavar=('HostName'),
                             dest='listhost',
                             default='host',
                             help='查询主机')
    parser_host.add_argument('--add-host',
                        dest='addhost',
                        nargs=4,
                        metavar=('192.168.2.1',
                                 'hostname_ceshi1', 
                                 'test01,test02', 
                                 'Template01,Template02'),
                        help='添加主机,多个主机组或模板使用分号')
    parser_host.add_argument('--disable',dest='disablehost',nargs=1,metavar=('hostname'),help='禁用主机')
    parser_host.add_argument('--delete',dest='deletehost',nargs=1,metavar=('hostnames'),help='删除主机,多个主机之间用分号')
    
    #####################################
    parser_report = parser.add_argument_group('report')
    parser_report.add_argument('--report',
                        nargs=3,
                        metavar=('item_name','date_from','date_till'),
                        dest='report',
                        help='eg:"CPU" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_available',
                        nargs=3,
                        metavar=('itemName','date_from','date_till'),
                        dest='report_available',
                        help='eg:"ping" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_available2',
                        nargs=2,
                        metavar=('date_from','date_till'),
                        dest='report_available2',
                        help='eg:"2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_flow',
                        nargs=2,
                        metavar=('date_from','date_till'),
                        dest='report_flow',
                        help='eg: "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    # template
    #####################################
    parser_template = parser.add_argument_group('template')
    parser_template.add_argument('--template',
                        nargs='?',
                        metavar=('TemplateName'),
                        dest='listtemp',
                        default='template',
                        help='查询模板信息')
    parser_template.add_argument('--template_import',
                        dest='template_import',
                        nargs=1,metavar=('templatePath'),
                        help='import template')
    # user
    #####################################
    parser_user = parser.add_argument_group('user')
    parser_user.add_argument('--usergroup',
                        nargs='?',
                        metavar=('name'),
                        default='usergroup',
                        dest='usergroup',
                        help='Inquire usergroup ID')
    parser_user.add_argument('--usergroup_add',
                        dest='usergroup_add',
                        nargs=2,
                        metavar=('usergroupName','hostgroupName'),
                        help='add usergroup')
    parser_user.add_argument('--usergroup_del',
                        dest='usergroup_del',
                        nargs=1,
                        metavar=('usergroupName'),
                        help='delete usergroup')
    parser_user.add_argument('--user',
                        nargs='?',
                        metavar=('name'),
                        default='user',
                        dest='user',
                        help='Inquire user ID')
    parser_user.add_argument('--user_add',
                        dest='user_add',
                        nargs=5,
                        metavar=("userName","userPassword","usergroupName","mediaName","email"),
                        help='add user')
    # mediatype
    #####################################
    parser_media = parser.add_argument_group('media')
    parser_media.add_argument('--mediatype',
                        nargs='?',
                        metavar=('name'),
                        default='mediatype',
                        dest='mediatype',
                        help='Inquire mediatype')
    parser_media.add_argument('--mediatype_add',
                        dest='mediatype_add',
                        nargs=2,
                        metavar=('mediaName','scriptName'),
                        help='add mediatype script')
    parser_media.add_argument('--mediatype_del',
                        dest='mediatype_del',
                        nargs=1,
                        metavar=('mediatypeName'),
                        help='delete mediatype')
    # drule
    #####################################
    parser_drule = parser.add_argument_group('drule')
    parser_drule.add_argument('--drule',
                        nargs='?',
                        metavar=('name'),
                        default='drule',
                        dest='drule',\
                        help='Inquire drule')
    parser_drule.add_argument('--drule_add',
                        dest='drule_add',
                        nargs=2,
                        metavar=('druleName','iprange'),\
                        help='add drule')
    parser_drule.add_argument('--drule_del',
                        dest='drule_del',
                        nargs=1,
                        metavar=('druleName'),
                        help='delete drule')
    # action
    #####################################
    parser_action = parser.add_argument_group('action')
    parser_action.add_argument('--action',
                        nargs='?',
                        metavar=('name'),
                        default='action',
                        dest='action',
                        help='Inquire action')
    parser_action.add_argument('--action_discovery_add',
                        dest='action_discovery_add',
                        nargs=2,
                        metavar=('actionName','hostgroupName'),\
                        help='add action')
    
    parser_action.add_argument('--action_autoreg_add',
                        dest='action_autoreg_add',
                        nargs=2,
                        metavar=('actionName','hostgroupName'),\
                        help='add action')

    # specialhost_get
    #####################################
    parser_condition = parser.add_argument_group('condition')
    parser_condition.add_argument('--hostgroupid',nargs=1,metavar=('hostgroupID'),dest='hostgroupid',\
            help='eg:"2,3,4"')
    parser_condition.add_argument('--hostid',nargs=1,metavar=('hostID'),dest='hostid',\
            help='eg:"10105,10106"')
    parser_condition.add_argument('--zero',dest='zero',default="OFF",help='入库时有0',action="store_true")
    
    #####################################
    parser_output = parser.add_argument_group('output_input')
    parser_output.add_argument('-f',nargs=1,metavar=('switch.file'),dest='switch_file',help='\
                        eg: "switch1.txt"')
    parser_output.add_argument('--table',dest='terminal_table',default="OFF",help='show the terminaltables',action="store_true")
    parser_output.add_argument('--xls',nargs=1,metavar=('xls_name.xls'),dest='xls',\
                        help='export data to xls')
    parser_output.add_argument('--title',nargs=1,metavar=('title_name'),dest='title',\
                        help="add the xls's title")
    parser_output.add_argument('--sort',nargs=1,metavar=('num'),dest='output_sort',default="OFF",help='设置第几列进行排序')
    parser_output.add_argument('--desc',dest='sort_reverse',default="OFF",help='排序设置为降序',action="store_true")
    
    parser.add_argument('--mysql',dest='mysql_quota',help='mysql使用空间',action="store_true")
    parser.add_argument('-v', action='version', version=__version__)
    parser.add_argument('--item',nargs='+',metavar=('HostID','item_name'),dest='listitem',help='查询item')
    parser.add_argument('--history',
                        nargs=3,
                        metavar=('item_id','time_from','time_till'),
                        dest='history',
                        help='eg:23298 "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser.add_argument('-d',dest='debug_output',default="OFF",help='show the debug info',action="store_true")
    # triggers
    #parser.add_argument('--triggers',nargs=1,metavar=('HostID'),dest='triggers_get',help='查询triggers')

    if len(sys.argv)==1:
        print parser.print_help()
    else:
        args=parser.parse_args()
        
        # 默认为普通输出格式
        terminal_table = False
        if args.terminal_table != "OFF":
            terminal_table = True
        
        # 默认不输出debug信息
        debug = False
        if args.debug_output != "OFF":
            debug = True
        
        # 值默认为入库值
        value_type = False
        if args.zero != "OFF":
            value_type = True
        
        # 输出结果默认不排序
        output_sort=False
        if args.output_sort != "OFF":
            output_sort = args.output_sort[0]
        
        # 默认排序方式为升序
        sort_reverse = False
        if args.sort_reverse != "OFF":
            sort_reverse = True


        zabbix=zabbix_api(terminal_table,debug,output_sort=output_sort,sort_reverse=sort_reverse)
        if args.mysql_quota:
            zabbix.mysql_quota()
        export_xls = {"xls":"OFF",
                      "xls_name":"ceshi.xls",
                      "title":"OFF",
                      "title_name":u"测试"
        }
        
        select_condition = {"hostgroupID":"",
                "hostID":""
                }

        # 导出报表
        if args.xls:
            export_xls["xls"] = 'ON'
            export_xls["xls_name"]=args.xls[0]
        if args.title:
            if export_xls["xls"] == "ON":
                export_xls["title"] = 'ON'
                export_xls["title_name"]=unicode(args.title[0],"utf-8")
            else:
                print "the title params invalid"
        if args.switch_file:
            hosts_file=args.switch_file[0]
        else:
            hosts_file="./switch"

        # 选择特定机器
        if args.hostgroupid:
            select_condition["hostgroupID"]=args.hostgroupid[0]
        if args.hostid:
            select_condition["hostID"] = args.hostid[0]

        if args.listhost != 'host' :
            if args.listhost:
                zabbix.host_get(args.listhost)
            else:
                zabbix.host_get()
        if args.listgroup !='group':
            if args.listgroup:
                zabbix.hostgroup_get(args.listgroup)
            else:
                zabbix.hostgroup_get()
        if args.usergroup != 'usergroup':
            if args.usergroup:
                zabbix.usergroup_get(args.usergroup)
            else:
                zabbix.usergroup_get()
        if args.mediatype != 'mediatype':
            if args.mediatype:
                zabbix.mediatype_get(args.mediatype)
            else:
                zabbix.mediatype_get()
        if args.listitem:
            if len(args.listitem) == 1:
                zabbix.item_get(args.listitem[0])
            else:
                zabbix.item_get(args.listitem[0],args.listitem[1])
        if args.history:
            zabbix.history(args.history[0],args.history[1],args.history[2])
        if args.report:
            zabbix.report(args.report[0],args.report[1],args.report[2],export_xls,select_condition)
        if args.report_flow:
            zabbix.report_flow(args.report_flow[0],args.report_flow[1],export_xls,hosts_file)
        if args.report_available:
            zabbix.report_available(args.report_available[0],args.report_available[1],args.report_available[2],export_xls,select_condition,value_type)
        if args.report_available2:
            zabbix.report_available2(args.report_available2[0],args.report_available2[1],export_xls,select_condition,value_type)
        if args.hostgroup_add:
            zabbix.hostgroup_create(args.hostgroup_add[0])
        if args.addhost:
            zabbix.host_create(args.addhost[0], args.addhost[1], args.addhost[2],args.addhost[3])
        ############
        # drule
        ############
        if args.drule != 'drule':
            if args.drule:
                zabbix.drule_get(args.drule)
            else:
                zabbix.drule_get()
        if args.drule_add:
            zabbix.drule_create(args.drule_add[0],\
                               args.drule_add[1]\
                              )
        ############
        # action
        ############
        if args.action != 'action':
            if args.action:
                zabbix.action_get(args.action)
            else:
                zabbix.action_get()
        if args.action_discovery_add:
            zabbix.action_discovery_create(args.action_discovery_add[0],\
                                           args.action_discovery_add[1]\
                              )
        if args.action_autoreg_add:
            zabbix.action_autoreg_create(args.action_autoreg_add[0],\
                                        args.action_autoreg_add[1]\
                              )
        ############
        # template
        ############
        if args.listtemp != 'template':
            if args.listtemp:
                zabbix.template_get(args.listtemp)
            else:
                zabbix.template_get()
        if args.template_import:
            with open(args.template_import[0], 'r') as f:
                template = f.read()
                try:
                    zabbix.configuration_import(template)
                except ZabbixAPIException as e:
                    print e
        ############
        # user
        ############
        if args.user != 'user':
            if args.user:
                zabbix.user_get(args.user)
            else:
                zabbix.user_get()
        if args.user_add:
            zabbix.user_create(args.user_add[0],\
                               args.user_add[1],\
                               args.user_add[2],\
                               args.user_add[3],\
                               args.user_add[4]
                              )
        ############
        # usergroup
        ############
        if args.usergroup_add:
            zabbix.usergroup_create(args.usergroup_add[0], args.usergroup_add[1])
        if args.usergroup_del:
            zabbix.usergroup_del(args.usergroup_del[0])
        ############
        # usergroup
        ############
        if args.mediatype_add:
            zabbix.mediatype_create(args.mediatype_add[0], args.mediatype_add[1])
        if args.mediatype_del:
            zabbix.mediatype_del(args.mediatype_del[0])
        if args.disablehost:
            zabbix.host_disable(args.disablehost)
        if args.deletehost:
            zabbix.host_delete(args.deletehost[0])
        ############
        # triggers
        ############
        #if args.triggers_get:
        #    zabbix.triggers_get(args.triggers_get[0])
