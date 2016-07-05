#!/usr/bin/python 
#coding:utf-8 
 
import json 
import urllib2 
from urllib2 import URLError 
import ConfigParser
import sys,argparse
import os
from colorclass import Color
from terminaltables import SingleTable
import my_sort
import time
import my_compare
import unicodedata
import XLSWriter
#{{{logging
import logging 
logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s%(message)s',
		datefmt='%a,%d %b %Y %H:%M:%S',
		filename='/tmp/zabbix.log',
		filemode='a')


#logging.debug('debug message')
#logging.info('info message')
#logging.warning('warning message')
#logging.error('error message')
#logging.critical('critical message')
#}}}
#{{{msg
def err_msg(msg):
    print "\033[41;37m[Error]: %s \033[0m"%msg
    exit()

  
def info_msg(msg):
    print "\033[42;37m[Info]: %s \033[0m"%msg

  
def warn_msg(msg):
    print "\033[43;37m[Warning]: %s \033[0m"%msg

#}}}
class zabbix_api: 
    def __init__(self,terminal_table): 
        if os.path.exists("zabbix_config.ini"):
            config = ConfigParser.ConfigParser()
            config.read("zabbix_config.ini")
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

    #{{{user_login
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
         
    #}}}
    # host
    #{{{host_get
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

    #}}}
    #{{{_host_get
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
                return 0
            for host in response['result']:      
                all_host_list.append((host['hostid'],host['host'],host['name']))
            return all_host_list

    #}}}
    #{{{host_create
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
            #print result.read()
            response = json.loads(result.read()) 
            result.close() 
            print "添加主机 : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (hostip, response['result']['hostids']) 


    #}}}
    #{{{host_disable
    def host_disable(self,hostip):
        data=json.dumps({
        "jsonrpc": "2.0",
        "method": "host.update",
        "params": {
        "hostid": self.host_get(hostip),
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
        print self.host_get(hostip)
                 
    #}}}
    #{{{host_delete
    def host_delete(self,hostid):
        hostid_list=[]
        #print type(hostid)
        for i in hostid.split(','):
            var = {}
            var['hostid'] = self.host_get(i)
            hostid_list.append(var)      
        print hostid_list
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "host.delete",
                "params": hostid_list,
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
            print "主机 \033[041m %s\033[0m  已经删除 !"%hostid 
    #}}}
    # hostgroup
    #{{{hostgroup_get(name)
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
                print "hostgroup:  \033[31m%s\033[0m\tgroupid : %s" %(group['name'],group['groupid'])
                self.hostgroupID = group['groupid'] 
                return group['groupid'] 

    #}}}
    #{{{_hostgroup_get_name(id)
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

    #}}}
    #{{{hostgroup_create
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


    #}}}
    # item
    #{{{item_get
    ##
    # @brief item_get 
    #
    # @param host_ID
    # @param itemName
    #
    # @return list
    # list_format [item['itemid'],item['name'],item['key_']]

    def item_get(self, host_ID='',itemName=''): 
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
            table_show.append(["itemid","name","key_"])
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
                    table_show.append([item['itemid'],item['name'],item['key_']])
                else:
                    if item['name']==itemName:
                        item_list.append([item['itemid'],item['name'],item['key_']])
                    else:
                        if my_compare.my_compare(item['name'],itemName):
                            item_list.append([item['itemid'],item['name'],item['key_']])
            
            if len(itemName) == 0:
                table=SingleTable(table_show)
                print(table.table)
            if len(item_list):
                return item_list
            else:
                return 0

    #}}}
    # report
    #{{{history_get(invalid)
    def history_get(self,history='',item_ID='',time_from='',time_till=''): 
        history_data=[]
        history_data[:]=[]
              
        #print history,item_ID,time_from,time_till     
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
            #print response
            result.close() 
            if len(response['result']) == 0:
                debug_info=str([history,item_ID,time_from,time_till,"####not have history_data"])
                logging.debug(debug_info)
                return 0.0,0.0,0.0
            for history_info in response['result']:
                history_data.append(history_info['value'])
            history_value=my_sort.Stats(history_data)
            history_min=history_value.min()
            #print history_min,type(history_min)
            history_max=history_value.max()
            #print history_max,type(history_max)
            history_avg=float('%0.4f'% history_value.avg())
            #print history_avg,type(history_avg)
            
            if history == '3':
                history_min = int(history_min)
                history_max = int(history_max)
                history_avg = int(history_avg)
            debug_info=str([history,item_ID,time_from,time_till,history_min,history_max,history_avg])
            logging.debug(debug_info)
            return (history_min,history_max,history_avg)

    #}}}
    #{{{_get_select_condition_info(select_condition)
    ##
    # @return 
    def _get_select_condition_info(self,select_condition): 
        output = ""
        if select_condition["hostgroupID"]:
            for i in select_condition["hostgroupID"].split(','):
                hostgroup_name = self._hostgroup_get_name(i)
                #print hostgroup_name
                output = hostgroup_name+u"、"+output
        if select_condition["hostID"]:
            host_name = self._host_get(hostID=select_condition["hostID"])
            for host_info in host_name:
                output = host_info[2]+u"、"+output
        return output
 #}}}
    #{{{report
    ##
    # @brief report 
    #
    # @param history
    # @param itemName
    # @param date_from
    # @param date_till
    # @param export_xls 
    #
    # @return 
    def report(self,history,itemName,date_from,date_till,export_xls,select_condition): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            info_msg=str(sheetName)
            logging.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01'] ['2016-06-01']")

        if export_xls["xls"] == 'ON':
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            if export_xls["title"] == 'ON':
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)

            xlswriter.add_header(u"报告周期:"+sheetName,6,sheet_name=sheetName)
            xlswriter.setcol_width([20,  20,20,10,10,10],sheet_name=sheetName)
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        if self.terminal_table:
            table_show=[]
            table_show.append(["hostid","name","itemName","min","max","avg"])
        else:
            print "hostid",'\t',"name",'\t',"itemName",'\t',"min",'\t',"max","avg"

        # 获取需要输出报表信息的host_list
        if select_condition["hostgroupID"] or select_condition["hostID"]:
            if export_xls["xls"] == 'ON':
                output_info = self._get_select_condition_info(select_condition)
                xlswriter.add_remark(u"范围:"+output_info,6,sheet_name=sheetName)
                xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern=True)
                
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
                xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern=True)
            host_list = self._host_get()
        for host_info in host_list: 
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                continue
            for itemid_sub_list in itemid_all_list:
                itemid=itemid_sub_list[0]
                item_name=itemid_sub_list[1]
                item_key=itemid_sub_list[2]
                debug_msg="itemid:%s"%itemid
                logging.debug(debug_msg)
                
                report_min,report_max,report_avg = self.trend_get(itemid,time_from,time_till)
                #history_min,history_max,history_avg = self.history_get(history,itemid,time_from,time_till)
                if history==3:
                    report_min=int(report_min)
                    report_max=int(report_max)
                    report_avg=int(report_avg)
                report_min=str(report_min)
                report_max=str(report_max)
                report_avg=str(report_avg)
                itemid=str(itemid)
                if self.terminal_table:
                    table_show.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
                else:
                    print host_info[0],'\t',host_info[2],'\t',itemid,item_name,'\t',report_min,'\t',report_max,'\t',report_avg
                if export_xls["xls"] == "ON":
                    xlswriter.writerow([host_info[0],host_info[2],item_name,report_min,report_max,report_avg],sheet_name=sheetName,border=True)
        print
        if self.terminal_table:
            table=SingleTable(table_show)
            table.title = itemName
            print(table.table)
        if export_xls["xls"] == 'ON':
            xlswriter.save()
        return 0
 #}}}
    #{{{agent_ping
    def agent_ping(self,item_ID='',time_from='',time_till=''): 
        history_data=[]
        history_data[:]=[]
              
        #print history,item_ID,time_from,time_till     
        #data = json.dumps({ 
        #                   "jsonrpc":"2.0", 
        #                   "method":"history.get", 
        #                   "params":{ 
        #                             "time_from":time_from,
        #                             "time_till":time_till,
        #                             "output": "extend",
        #                             "history": 3,
        #                             "itemids": item_ID,
        #                             "sortfield":"clock",
        #                             "limit": 10080
        #                             }, 
        #                   "auth":self.user_login(), 
        #                   "id":1, 
        #                   }) 
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
                debug_info=str([item_ID,time_from,time_till,"####not have history_data"])
                logging.debug(debug_info)
                return 0,0
            sum_value = 0
            for result_info in response['result']:
                hour_num_string = unicodedata.normalize('NFKD',result_info['num']).encode('ascii','ignore')
                hour_num=eval(hour_num_string)
                sum_value = sum_value + hour_num
                debug_info=str([result_info['num']])
                logging.debug(debug_info)
            trend_sum = len(response['result'])
            return trend_sum,sum_value

    #}}}
    #{{{report_available
    ##
    # @brief report_available
    #
    # @param history
    # @param itemName
    # @param date_from
    # @param date_till
    # @param export_xls
    #
    # @return 
    def report_available(self,itemName,date_from,date_till,export_xls,select_condition): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        check_time=60
        hour_check_num = int(3600/check_time)
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            info_msg=str(sheetName)
            logging.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01'] ['2016-06-01']")

        if export_xls["xls"] == 'ON':
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            if export_xls["title"] == 'ON':
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
            xlswriter.add_header(u"报告周期:"+sheetName,6,sheet_name=sheetName)
            xlswriter.setcol_width([20,20,20,10,10,10],sheet_name=sheetName)
            xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern=True)
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
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
                xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern=True)
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
                xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern=True)
            host_list = self._host_get()
        for host_info in host_list: 
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                continue
            for itemid_sub_list in itemid_all_list:
                
                itemid=itemid_sub_list[0]
                item_name=itemid_sub_list[1]
                item_key=itemid_sub_list[2]
                debug_msg="itemid:%s"%itemid
                logging.debug(debug_msg)
                
                #history_min,history_max,history_avg = self.agent_ping(itemid,time_from,time_till)
                trend_sum,sum_value = self.agent_ping(itemid,time_from,time_till)
                if (sum_value > 0) and (trend_sum > 0):
                    sum_value = float(sum_value*100)
                    sum_check=trend_sum*hour_check_num
                    avg_ping=sum_value/sum_check
                    if avg_ping == 100:
                        avg_ping =int(avg_ping)
                    else:
                        avg_ping=float('%0.2f'% avg_ping)
                    diff_ping = avg_ping - 100

                if self.terminal_table:
                    table_show.append([host_info[0],host_info[2],itemName,"100",str(avg_ping),str(diff_ping)])
                else:
                    print host_info[0],'\t',host_info[2],'\t',itemName,'\t',"100",'\t',avg_ping,'\t',diff_ping
                if export_xls["xls"] == "ON":
                    xlswriter.writerow([host_info[0],host_info[2],itemName,"100",str(avg_ping),str(diff_ping)],sheet_name=sheetName,border=True)
        print
        if self.terminal_table:
            table=SingleTable(table_show)
            table.title = itemName
            print(table.table)
        if export_xls["xls"] == 'ON':
            xlswriter.save()
        return 0
 #}}}
    #{{{alert_get
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
    #}}}
    #{{{trend_get
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
                           "time_from":time_from,
                           "time_till":time_till,
                           "params":{ 
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
                logging.debug(debug_info)
                return 0.0,0.0,0.0
            for result_info in response['result']:
                #print type(result_info['value_min'])
                #if not cmp(result_info['value_min'], '0.0'):
                #if result_info['value_min'] == "0.0000":
                #    print result_info['value_min']
                #    debug_info=str([result_info])
                #    logging.debug(debug_info)
                #else:
                #    trend_min_data.append(result_info['value_min'])
                trend_min_data.append(result_info['value_min'])
                    
                trend_max_data.append(result_info['value_max'])
                trend_avg_data.append(result_info['value_avg'])
            trend_min_data_all=my_sort.Stats(trend_min_data)
            trend_max_data_all=my_sort.Stats(trend_max_data)
            trend_avg_data_all=my_sort.Stats(trend_avg_data)
            #print trend_min_data
            #print trend_max_data
            #print trend_avg_data
            trend_min=trend_min_data_all.min()
            trend_max=trend_max_data_all.max()
            trend_avg=float('%0.4f'% trend_avg_data_all.avg())
            
            #if history == '3':
            #    history_min = int(history_min)
            #    history_max = int(history_max)
            #    history_avg = int(history_avg)
            #debug_info=str([history,item_ID,time_from,time_till,history_min,history_max,history_avg])
            #logging.debug(debug_info)
            return (trend_min,trend_max,trend_avg)
    #}}}
    # template
    #{{{template_get
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
            else:
                print "template","id"
            result.close() 
            #print response
            for template in response['result']:                
                if len(templateName)==0:
                    if self.terminal_table:
                        table_show.append([template['name'],template['templateid']])
                    else:
                        print "template : \033[31m%s\033[0m\t  id : %s" % (template['name'], template['templateid'])
                else:
                    self.templateID = response['result'][0]['templateid'] 
                    print "Template Name :  \033[31m%s\033[0m "%templateName
                    return response['result'][0]['templateid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    #}}}
    #{{{configuration
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
    #}}}
    # user
    #{{{user_get
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
    #}}}
    #{{{user_create
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
    #}}}
    # usergroup
    #{{{usergroup_get
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
    #}}}
    #{{{usergroup_create
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
    #}}}
    #{{{usergroup_del
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
    #}}}
    # mediatype
    #{{{mediatype_get
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
    #}}}
    #{{{mediatype_create
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
    #}}}
    #{{{mediatype_del
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
    #}}}
    # drule(discoveryRules)
    #{{{drule_get
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
    #}}}
    #{{{drule_create
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
    #}}}
    # action
    # eventsource 0 triggers
    # eventsource 1 discovery
    # eventsource 2 auto registration
    # eventsource 3 internal
    #{{{action_get
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
            print "drule sum: \033[31m%s\033[0m"%(len(response['result']))
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
                    return action['druleid']
            if self.terminal_table:
                table=SingleTable(table_show)
                print(table.table)
    #}}}
    #{{{action_discovery_create
    def action_discovery_create(self, actionName,hostgroupName): 
        if self.drule_get(actionName):
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
    #}}}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='zabbix  api ',usage='%(prog)s [options]')
    parser.add_argument('-G','--group',nargs='?',metavar=('GroupName'),dest='listgroup',default='group',help='查询主机组')
    parser.add_argument('--hostgroup_add',nargs=1,dest='hostgroup_add',help='添加主机组')
    parser.add_argument('-H','--host',nargs='?',metavar=('HostName'),dest='listhost',default='host',help='查询主机')
    parser.add_argument('--item',nargs='+',metavar=('HostID','item_name'),dest='listitem',help='查询item')
    parser.add_argument('--history_get',nargs=4,metavar=('history_type','item_ID','time_from','time_till'),dest='history_get',help='查询history')
    parser.add_argument('--report',nargs=4,metavar=('history_type','item_name','date_from','date_till'),dest='report',help='\
                        eg: 0 "CPU" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser.add_argument('--report_available',nargs=3,metavar=('itemName','date_from','date_till'),dest='report_available',help='\
                        eg:"Agent ping" "2016-06-03" "2016-06-10"')
    parser.add_argument('--table',nargs='?',metavar=('ON'),dest='terminal_table',default="OFF",help='show the terminaltables')
    parser.add_argument('--xls',nargs=1,metavar=('xls_name.xls'),dest='xls',\
                        help='export data to xls')
    parser.add_argument('--title',nargs=1,metavar=('title_name'),dest='title',\
                        help="add the xls's title")
    #parser.add_argument('--trend_get',nargs=1,metavar=('item_ID'),dest='trend_get',help='查询item trend')
    # template
    parser.add_argument('-T','--template',nargs='?',metavar=('TemplateName'),dest='listtemp',default='template',help='查询模板信息')
    parser.add_argument('--template_import',dest='template_import',nargs=1,metavar=('templatePath'),help='import template')
    # user
    parser.add_argument('--usergroup',nargs='?',metavar=('name'),default='usergroup',dest='usergroup',help='Inquire usergroup ID')
    parser.add_argument('--usergroup_add',dest='usergroup_add',nargs=2,metavar=('usergroupName','hostgroupName'),help='add usergroup')
    parser.add_argument('--usergroup_del',dest='usergroup_del',nargs=1,metavar=('usergroupName'),help='delete usergroup')
    parser.add_argument('--user',nargs='?',metavar=('name'),default='user',dest='user',help='Inquire user ID')
    parser.add_argument('--user_add',dest='user_add',nargs=5,metavar=("userName","userPassword","usergroupName","mediaName","email"),help='add user')
    # mediatype
    parser.add_argument('--mediatype',nargs='?',metavar=('name'),default='mediatype',dest='mediatype',help='Inquire mediatype')
    parser.add_argument('--mediatype_add',dest='mediatype_add',nargs=2,metavar=('mediaName','scriptName'),help='add mediatype script')
    parser.add_argument('--mediatype_del',dest='mediatype_del',nargs=1,metavar=('mediatypeName'),help='delete mediatype')
    # drule
    parser.add_argument('--drule',nargs='?',metavar=('name'),default='drule',dest='drule',\
                        help='Inquire drule')
    parser.add_argument('--drule_add',dest='drule_add',nargs=2,metavar=('druleName','iprange'),\
                        help='add drule')
    parser.add_argument('--drule_del',dest='drule_del',nargs=1,metavar=('druleName'),\
                        help='delete drule')
    # action
    parser.add_argument('--action',nargs='?',metavar=('name'),default='action',dest='action',\
                        help='Inquire action')
    parser.add_argument('--action_discovery_add',dest='action_discovery_add',nargs=2,metavar=('actionName','hostgroupName'),\
                        help='add action')

    # specialhost_get
    parser.add_argument('--hostgroupid',nargs=1,metavar=('hostgroupID'),dest='hostgroupid',\
            help='eg:"2,3,4"')
    parser.add_argument('--hostid',nargs=1,metavar=('hostID'),dest='hostid',\
            help='eg:"10105,10106"')
    parser.add_argument('-C','--add-host',dest='addhost',nargs=4,metavar=('192.168.2.1','hostname_ceshi1', 'test01,test02', 'Template01,Template02'),help='添加主机,多个主机组或模板使用分号')
    parser.add_argument('-d','--disable',dest='disablehost',nargs=1,metavar=('192.168.2.1'),help='禁用主机')
    parser.add_argument('-D','--delete',dest='deletehost',nargs='+',metavar=('192.168.2.1'),help='删除主机,多个主机之间用分号')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0.7')
    if len(sys.argv)==1:
        print parser.print_help()
    else:
        args=parser.parse_args()
        terminal_table = False
        if args.terminal_table != "OFF":
            terminal_table = True
        zabbix=zabbix_api(terminal_table)
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
        if args.history_get:
            zabbix.history_get(args.history_get[0],args.history_get[1],args.history_get[2],args.history_get[3])
        if args.report:
            zabbix.report(args.report[0],args.report[1],args.report[2],args.report[3],export_xls,select_condition)
        if args.report_available:
            zabbix.report_available(args.report_available[0],args.report_available[1],args.report_available[2],export_xls,select_condition)
        if args.hostgroup_add:
            zabbix.hostgroup_create(args.hostgroup_add[0])
        if args.addhost:
            zabbix.host_create(args.addhost[0], args.addhost[1], args.addhost[2])
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
