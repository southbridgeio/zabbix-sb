#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '1.0'

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


# Define zabbix config file

zbx_conf_file = os.path.dirname(os.path.realpath(__file__)) + '/../conf/zabbix.conf'

# Get zabbix server connect credentials

for tmp_line in open(zbx_conf_file):
    if "server" in tmp_line: zbx_server = str(tmp_line.split("=")[1]).rstrip()
    if "user" in tmp_line: zbx_user = str(tmp_line.split("=")[1]).rstrip()
    if "pass" in tmp_line: zbx_pass = str(tmp_line.split("=")[1]).rstrip()

# Connect to server

zapi = ZabbixAPI(zbx_server)
zapi.login(zbx_user, zbx_pass)

# Define git update module

execfile(os.path.dirname(os.path.realpath(__file__)) + '/../git_update.py')

# Try to get update from git

if git_check_update(os.path.dirname(os.path.realpath(__file__))) == 1:
    # if not up to day update and exit
    exit(0)

parser = argparse.ArgumentParser(description='Arguments to web test in zabbix')
parser.add_argument('--prname', required=True, action='store', default=None, dest='proj',
                    help='Project name in zabbix. For example: southbridge.ru')
args = parser.parse_args()

project_name = args.proj

# Find and remove autoregistration actions

zbx_action = zapi.action.get(
    {
        "search" : {"name": project_name}
    }
)

for action in zbx_action:
    zapi.action.delete ([action['actionid']])

if zbx_action:
    print ("Auto registration action deleted [Ok]")
else:
    print("Auto registration dosen't exist")

zbx_host_group = zapi.hostgroup.get(
    {
        "output": "extend",
        "filter":
            {

                "name": [project_name]

            }

    }
)
# Find and remove host and host groups
if zbx_host_group:
    host_get = zapi.host.get(
       {
           "output": "shorten",
           "selectGroups": "shorten",
           'groupids': [zbx_host_group[0]['groupid']]

        }
    )
    for host in host_get:
        zbx_host_del = zapi.host.delete ([host['hostid']])
    if host_get:
        print("All host deleted from group [Ok]")
    else:
        print("Host in group dosen't exist")

    zbx_host_group = zapi.hostgroup.delete([zbx_host_group[0]['groupid']])
    print("Project group deleted [Ok]")
else:
    print("Project " + project_name + " dosen't exist")


# Find and remove  project users 
zbx_usergroup = zapi.usergroup.get (
    {
        "output": "extend",
        "filter":
            {

                "name": [ project_name ]

            }

    }

)


if zbx_usergroup:
    zbx_user = zapi.user.get(
        {
            "output": "shorten",
            "selectUsrgrps": "shorten",
            'usrgrpids': zbx_usergroup[0]['usrgrpid']
        }
    )
    if zbx_user:
        for user in zbx_user:
            zapi.user.delete ([user['userid']])
            print("All users deleted from user group [Ok]")
    else:
        print ("Users in user group dosen't exist")
    zapi.usergroup.delete ([zbx_usergroup[0]['usrgrpid']])
    print("User group deleted [Ok]")
else:
    print("User group dosen't exist")

print ("All settings of project deledet sucsesfull")

