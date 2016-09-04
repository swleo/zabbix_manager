#!/usr/bin/env python
#coding=utf8
"""
# Author: Bill
# Created Time : Wed 02 Dec 2015 10:17:28 AM CST

# File Name: wb_zabbix.py
# Description:

"""
__version__ = '1.1.1'

import ConfigParser
import subprocess
import snack
import sys
import os
from zabbix_api import zabbix_api

# Set Working Directory
abspath = os.path.realpath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# Get console size to help with formatting
r, c = os.popen('stty size', 'r').read().split()

class Zabbix_tool:
    def __init__(self):
        if os.path.exists("zabbix_config.ini"):
            config = ConfigParser.ConfigParser()
            config.read("zabbix_config.ini")
            self.support = config.get("gui", "support")
            #self.output_debug = config.get("gui", "output_debug")
        else:
            sys.exit("Settings file not found.. exiting.")
        self.screen = snack.SnackScreen()
        self.screen.drawRootText(1, 1, "Zabbix tool%s"
                                 % __version__)
        self.screen.drawRootText(int(c) - (10 + len(self.support)),
                                 int(r) - 2,
                                 "Support: %s" % self.support)
        self.screen.refresh()
        self.task_type = None
        self.action = None
        self.task_info = None
        self.task_usermod = None
        self.task_modcmt = None
        self.task_grpmod = None
        self.task_hosts = None
        self.task_hostsind = None
        self.user_comment = None
        self.task_debug = None

    def reset_task(self):
        dic = vars(self)
        skip = ['screen']
        for i in dic.keys():
            if i not in skip:
                dic[i] = None

    def exit_menu(self):
        pass
    
    # 一级menu
    def get_task(self):
        self.reset_task()
        i = snack.ListboxChoiceWindow(self.screen,
                                      "Select Task",
                                      "",
                                      [('action_create',
                                        ('action_create', 'action_create'))
                                      ],
                                      buttons=['Exit'], width=65)

        if i and i[0] != 'exit':
            self.task_type = i[1]
            if task.task_type[1] == 'action_create':
                task.action_create()
            elif task.task_type[1] == 'task_2':
                task.user_info()
            elif task.task_type[1] == 'task_3':
                task.mod_user()
            elif task.task_type[1] == 'task_4':
                task.set_user()
                self.set_hosts()
        else:
            self.exit_menu()

    # 2
    def action_create(self):
        i = snack.EntryWindow(self.screen,
                              self.task_type[0],
                              "Please enter action Information",
                              ["action_name ",
                               "group_name"],
                              buttons=['Ok', 'Back'],
                              width=65, entryWidth=40)
        if i[0] != 'back':
            self.action = i
            action_name=self.action[1][0]
            group_name=self.action[1][1]
            zabbix=zabbix_api(False,False,output=False)
            info = zabbix.action_autoreg_create(action_name,group_name)
            info_dirt=eval(info)
            snack.ButtonChoiceWindow(self.screen,
                                                 "%s" % self.task_type[0],
                                                 "Info:\n\n"
                                                 "%s: %s"
                                                 % (info_dirt["status"],info_dirt["output"]),
                                                 buttons=['Ok'],
                                                 width=65)
                
            self.get_task()
        else:
            self.get_task()

    def user_info(self):
        self.set_user()
        i = snack.ListboxChoiceWindow(self.screen,
                                      self.task_type[0],
                                      "Select Task",
                                      [("Check User's Group Membership",
                                        ("Check User's Group Membership",
                                         "check_group"))],
                                      buttons=['Ok', 'Back'], width=65)
        if i[0] != 'back':
            self.task_info = i
            self.set_hosts()
        else:
            self.get_task()

    def mod_user(self):
        self.task_usermod = None
        self.task_grpmod = None
        self.task_modcmt = None
        i = snack.ListboxChoiceWindow(self.screen,
                                      self.task_type[0],
                                      "Pick a User Modification Task",
                                      [("Add Group Membership", "addgrp"),
                                       ("Remove Group Membership", "remgrp"),
                                       ("Modify Account Comment", "modcmt")],
                                      buttons=['Ok', 'Back'], width=65)
        if i[0] != 'back':
            self.task_usermod = i
            if i[1] in ['addgrp', 'remgrp']:
                self.set_user()
                grp = snack.EntryWindow(self.screen,
                                        self.task_type[0],
                                        "Provide Groups: "
                                        "(ie: group1,group2,group3)\n",
                                        ["Groups: "],
                                        buttons=['Ok', 'Back'],
                                        width=65, entryWidth=40)
                if grp[0] != 'back':
                    self.task_grpmod = grp
                    self.set_hosts()
                else:
                    self.mod_user()

            elif i[1] == 'modcmt':
                self.set_user()
                cmt = snack.EntryWindow(self.screen,
                                        self.task_type[0],
                                        "Update info for %s"
                                        % self.task_user[1][0],
                                        ["First Name",
                                         "Last Name",
                                         ("Company/Department",
                                          lugms_settings.company),
                                         ("Phone Number",
                                          lugms_settings.phone),
                                         ("Accnt Type",
                                          lugms_settings.acct_type)],
                                        buttons=['Ok', 'Back'],
                                        width=65, entryWidth=40)
                if cmt[0] != 'back':
                    self.task_modcmt = cmt
                    cstring = str()
                    for v in self.task_modcmt[1]:
                        if v.strip():
                            cstring = cstring + v + " "
                    self.user_comment = cstring.rstrip()
                    self.set_hosts()
                else:
                    self.mod_user()
        else:
            self.get_task()

    def set_user(self):
        i = snack.EntryWindow(self.screen,
                              self.task_type[0],
                              "Please enter User ID",
                              ["User ID: "],
                              buttons=['Ok', 'Back'],
                              width=65, entryWidth=20)
        if i[0] != 'back':
            self.task_user = i
        else:
            self.get_task()

    # 3
    def set_hosts(self, val=None):
        i = snack.ListboxChoiceWindow(self.screen,
                                      self.task_type[0],
                                      "Select Servers",
                                      [('Specific Servers', "hosts_ind"),
                                       ('All Linux Servers', 'hosts_all')],
                                      buttons=['Ok', 'Back'], width=65)
        if i[0] != 'back':
            self.task_hosts = i
            if i[1] == 'hosts_ind':
                if val:
                    ind = snack.EntryWindow(self.screen,
                                            self.task_type[0],
                                            "Provide Hostnames: "
                                            "(ie: server1,server2,server3)",
                                            [("Hosts: ", val)],
                                            buttons=['Ok', 'Back'],
                                            width=65, entryWidth=40)
                else:
                    ind = snack.EntryWindow(self.screen,
                                            self.task_type[0],
                                            "Provide Host Names\n"
                                            "ie: server1,server2,server3",
                                            ["Hosts: "],
                                            buttons=['Ok', 'Back'],
                                            width=65, entryWidth=40)
                if ind[0] != 'back' and len(ind[1][0].split(',')) >= 1:
                    taskhosts = str()
                    invalhosts = str()
                    hostlist = ind[1][0].split(',')
                    hostlist = list(set(hostlist))
                    hostlist.sort()
                    for host in hostlist:
                        if host in validhosts:
                            taskhosts = taskhosts + (host + ',')
                        else:
                            invalhosts = invalhosts + (host + ',')
                    taskhosts = taskhosts.rstrip(",")
                    invalhosts = invalhosts.rstrip(",")
                    if taskhosts == '':
                        snack.ButtonChoiceWindow(self.screen,
                                                 self.task_type[0],
                                                 "No Valid Hostnames Provided",
                                                 buttons=['Ok'], width=65)
                        self.set_hosts()
                    elif len(invalhosts) > 1:
                        snack.ButtonChoiceWindow(self.screen,
                                                 self.task_type[0],
                                                 "Valid hostnames: %s\n"
                                                 "\nInvalid hostnames: %s\n"
                                                 "\nPlease re-verify hosts.."
                                                 % (taskhosts, invalhosts),
                                                 buttons=['Verify Hosts'],
                                                 width=65)
                        self.set_hosts(taskhosts)
                    else:
                        self.task_hostsind = ind
                else:
                    self.set_hosts()
        else:
            self.get_task()


    def finish(self):

        self.screen.finish()
        if os.path.exists("zabbix_config.ini"):
            config = ConfigParser.ConfigParser()
            config.read("zabbix_config.ini")
            output_debug = config.get("gui", "output_debug")
        else:
            sys.exit("Settings file not found.. exiting.")
        #if 1:
        if output_debug != "False":
            attrs = vars(task)
            print ''.join("%s: %s\n" % item for item in attrs.items())


if __name__ == '__main__':
    task = Zabbix_tool()
    #task.get_task()
    try:
        task.get_task()
    except Exception as e:
        task.finish()
        sys.exit("Exit with exception: %s" % e)
    task.finish()
    print('\nDone.')
