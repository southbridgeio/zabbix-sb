#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '1.2'

from zabbix_api import ZabbixAPI
import os
import argparse
import datetime

#Define git update module

execfile(os.path.dirname(os.path.realpath(__file__)) + '/../git_update.py')

#Try to get update from git

if git_check_update(os.path.dirname(os.path.realpath(__file__))) == 1:
    # if not up to day update and exit
    exit (0)

#Define zabbix config file

zbx_conf_file =os.path.dirname(os.path.realpath(__file__)) + '/../conf/zabbix.conf'

# Get zabbix server connect credentials
for tmp_line in open(zbx_conf_file):
    if "server" in tmp_line: zbx_server = str(tmp_line.split("=")[1]).rstrip()
    if "user" in tmp_line: zbx_user = str(tmp_line.split("=")[1]).rstrip()
    if "pass" in tmp_line: zbx_pass = str(tmp_line.split("=")[1]).rstrip()

# Connect to zabbix server
zapi = ZabbixAPI(zbx_server)
zapi.login(zbx_user,zbx_pass)

parser = argparse.ArgumentParser(description='Arguments to web test in zabbix')
parser.add_argument('--url', required=True, action='store', default=None, dest='url', help='Site url. Example: http://test.com')
parser.add_argument('--pattern', required=True, action='store', default=None, dest='pattern', help='Required pattern on site ')
parser.add_argument('-p','--prname',action='store', required=True, default='None', dest='Pr_Name', help='Project name in zabbix ' )
parser.add_argument('--desc', required=True, action='store', default=None, dest='desc', help='Desc about this web test')
args =  parser.parse_args()

url = args.url
pattern = args.pattern
desc = args.desc
pr_name = args.Pr_Name
name = url[:40]

zbx_host_get = zapi.host.get(
    {
        # "output": "extend",
        "search":
            {
                "host": "content_check." + pr_name
            }
    }

)

if not zbx_host_get:
        print ("Special host dose not exist")
        exit (0)
else:
        zbx_interface = zapi.hostinterface.get ({"hostids":zbx_host_get[0]['hostid']})


if zbx_host_get:

        result = zapi.httptest.get({
                                "filter": { "name":["check content " +  name]},
                                "output": "extend",
                                "hostid": zbx_host_get[0]['hostid']

                            }
                        )


        if result:
                print("Web test  already exist!")
                exit (0)




result = zapi.httptest.create({
                                "name": "check content " +  name,
                                "hostid": zbx_host_get[0]['hostid'],
                                "variables":"",
                                "headers":'',
                                "posts":'',
                                "delay":20,
                                "steps": [
                                    {
                                        "name": "Base",
                                        "url": url ,
                                        "status_codes": 200,
                                        "headers":'',
                                        "posts":'',
                                        "variables":'',
                                        "timeout":30,
                                        "required": pattern,
                                        "no": 1
                                    }
                                ]
                            }
                        )

result = zapi.trigger.create (
    {
        "description":"Attention! Check content " + name +" failed!",
        "expression":"{content_check." + pr_name + ":web.test.fail[check content " + name + "].count(#3,0,\"ne\")}=3 and {content_check." + pr_name + ":web.test.error[check content " + name + "].str(000000000000)}=0",
        "priority": 5,
        "comments" : desc,
        "url": url


    }

)

print ("Web check successful create: [Ok]")


url = name


if 'https' in  url.split('/')[0]:
    domainName = url.split('/')[2].split('?')[0]

    zbx_item = zapi.item.get(
        {
            "output": "extend",
            "hostids": zbx_host_get[0]['hostid'],
            "filter":
                {
                    "name": "ssl expiration " + domainName
                }
        }

    )

    if not zbx_item:
        zbx_item = zapi.item.create(
            {
                "name": "ssl expiration " + domainName,
                "key_": "ssl_exp[" + domainName + "]",
                "hostid": zbx_host_get[0]['hostid'],
                "interfaceid": zbx_interface[0]['interfaceid'],
                "type": 0,
                "value_type": 3,
                "delay": 30

            }
        )
        print("Items certificate check  create: [OK]")

        if zbx_item:
            zab_trigger = zapi.trigger.create(
                {
                    "description": "SSL certificate for " + domainName + " expires in 20 days",
                    "expression": "{content_check." + pr_name + ":ssl_exp[" + domainName + "].last()}=20",
                    "comments": "",
                    "url": "http://" + domainName,
                    "priority": "4"
                }
            )
            print("Trigger certificate check create: [OK]")
    else:
        print("Certificate check already exist: [OK]")
