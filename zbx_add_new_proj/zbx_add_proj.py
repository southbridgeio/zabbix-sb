#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '2.1'

import argparse
import random
import os
from zabbix_api import ZabbixAPI

def password(pw_length):
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]
    return (mypw)


#Define zabbix config file

zbx_conf_file =os.path.dirname(os.path.realpath(__file__)) + '/../conf/zabbix.conf'

# Get zabbix server connect credentials

for tmp_line in open(zbx_conf_file):
    if "server" in tmp_line: zbx_server = str(tmp_line.split("=")[1]).rstrip()
    if "user" in tmp_line: zbx_user = str(tmp_line.split("=")[1]).rstrip()
    if "pass" in tmp_line: zbx_pass = str(tmp_line.split("=")[1]).rstrip()

# Connect to server

zapi = ZabbixAPI(zbx_server)
zapi.login(zbx_user,zbx_pass)

# Define git update module

execfile(os.path.dirname(os.path.realpath(__file__)) + '/../git_update.py')

#Try to get update from git

if git_check_update(os.path.dirname(os.path.realpath(__file__))) == 1:
    # if not up to day update and exit
    exit (0)

parser = argparse.ArgumentParser(description='Arguments to web test in zabbix')
parser.add_argument('--prname', required=True, action='store', default=None, dest='proj', help='Project name in redmine. For example: southbridge.ru')
args =  parser.parse_args()


project_name = args.proj

result = zapi.hostgroup.get (
    {
        "output": "extend",
        "filter":
            {

                "name": [ project_name ]

            }

    }
)



if result:
    print ("Project " + project_name + " already exist!")
    exit (0)

hostgroup = zapi.hostgroup.create (
    {
        "name": project_name
    }
)


print ("Группа создана\n")

zbx_host_icmp = zapi.host.create(
    {
        "host": "icmp_rus." + project_name,
        "proxy_hostid": 568884,
        "interfaces":
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "139.59.156.212",
                "dns": "",
                "port": "10050"
            },
        "groups": [
            {
                "groupid": int(hostgroup['groupids'][0])
            }
        ],
        "templates":
            [
                {
                    "templateid": "568887"
                }
            ]

    }

)


zbx_macro_add = zapi.usermacro.create(
    {
        "hostid": int(zbx_host_icmp["hostids"][0]),
        "macro": "{$HG}",
        "value": project_name
    }
)


zbx_host_content = zapi.host.create(
    {
        "host": "content_check." + project_name,
        "interfaces":
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "127.0.0.1",
                "dns": "",
                "port": "10050"
            },
        "groups": [
            {
                "groupid": int(hostgroup['groupids'][0])
            },
	    {
	    	"groupid": 144
	    }
        ]
        

    }

)

if zbx_host_content and zbx_host_icmp:
    print ("Служебные хосты созданы\n")

hostgroup = hostgroup['groupids'][0]



result = zapi.action.create ( {
                                    "name":'Auto registration ds.' + project_name,
                                    "eventsource":2,
                                    "def_shortdata":'Auto registration: {HOST.HOST}',
                                    "def_longdata": '',
                                    "r_longdata":" ",
                                    "filter": {
                                        "evaltype": 0,
                                        "conditions":[
                                                 {
                                                    "conditiontype":"24",
                                                    "operator": "2" ,
                                                    "value": "ds." + project_name
                                                }
                                            ],
                                        },
                                    "operations": [
                                        {
                                            "operationtype":4,
                                            "opgroup" : [{"groupid": hostgroup}]
                                        },
                                        {
                                            "operationtype":2
                                        },
                                        {
                                            "operationtype":6,
                                            "optemplate":[{"templateid":"10001" },{"templateid":"10106"}, {"templateid":"10112"} ]
                                        },

                                    ]

                            }

)


result = zapi.action.create ( {
                                    "name":'Auto registration vs.' + project_name,
                                    "eventsource":2,
                                    "def_shortdata":'Auto registration: {HOST.HOST}',
                                    "def_longdata": '',
                                    "r_longdata":" ",
                                    "filter": {
                                        "evaltype": 0,
                                        "conditions":[
                                                 {
                                                    "conditiontype":"24",
                                                    "operator": "2" ,
                                                    "value": "vs." + project_name
                                                }
                                            ],
                                        },
                                    "operations": [
                                        {
                                            "operationtype":4,
                                            "opgroup" : [{"groupid": hostgroup}]
                                        },
                                        {
                                            "operationtype":2
                                        },
                                        {
                                            "operationtype":6,
                                            "optemplate":[{"templateid":"10001" }]
                                        },

                                    ]

                            }

)


print ("Правила авторегистрации создано.\n")


usergroup = zapi.usergroup.get (
    {
        "output": "extend",
        "filter":
            {

                "name": [ project_name ]

            }

    }

)
if usergroup:
     print ("User group " + project_name + " already exist!")
else:
    usergroup = zapi.usergroup.create(
        {
            "name":project_name,
            "rights":
                {
                    "permission": 2,
                    "id": hostgroup
                }
        }
    )
    if usergroup:
        user = zapi.user.get (
            {
                "output": "extend",
                "filter":
                        {

                            "name": [ project_name ]

                         }

            }
        )

        if user:
            print ("User " + project_name + " already exist!")
        else:
            zbx_pass = password(10)
            user = zapi.user.create(
                {
                    "alias": project_name,
                    "passwd": zbx_pass,
                    "usrgrps": usergroup['usrgrpids'][0]

                }
            )
            if user:
                print ("Не забудте занести учетные данные пользователя, для доступа к zabbix, в wiki:\n")
                print ("h2. Система мониторинга\n\n" 
                       + "host: zabbix.southbridge.ru\n" 
                       + "user: " + project_name + "\n" 
                       + "pass: " + zbx_pass)
            else:
                print ('Не удалось создать пользователя.')
