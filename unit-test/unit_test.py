#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '1.0'

import datetime
import os
from zabbix_api import ZabbixAPI


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

zbx_group_get = zapi.hostgroup.get(
    {
        "search":
            {
                "name": "autotest.southbridge.io"
            }
    }
)

if not zbx_group_get:
    print "Group autotest.southbridge.io not found. Test failed"
    raise SystemExit(1)



zbx_host_get = zapi.host.get(
    {
        "search":
            {
                "name": "icmp_rus.autotest.southbridge.io"
            }
    }
)

if not zbx_host_get:
    print "Host icmp_rus.autotest.southbridge.io not found. Test failed"
    raise SystemExit(1)
    
zbx_host_get = zapi.host.get(
    {
        "search":
            {
                "name": "content_check.autotest.southbridge.io"
            }
    }
)

if not zbx_host_get:
    print "Host content_check.autotest.southbridge.io not found. Test failed"
    raise SystemExit(1)
else:
    web_test_without_trigger = ""
    zbx_w = zapi.httptest.get({"filter": {"hostid": zbx_host_get[0]['hostid']}})
    if zbx_w:
            for web_test in zbx_w:
                    trigger_name = web_test['name'].replace("check content ", "")
                    trigger_name = trigger_name.replace(" ", "")
                    zbx_trigger = zapi.trigger.get(
                           {
                                "output": "extend",
                                "hostid":  zbx_host_get[0]['hostid'],
                                "search": {"description":  trigger_name },
                            }
                        )
                    if not zbx_trigger:
                        web_test_without_trigger = 1
    else:
        print "Web check not found. Test failed"
        raise SystemExit(1)
        
if len(web_test_without_trigger) > 0:
    print "Trigger for web check not found. Test failed"
    raise SystemExit(1)

zbx_usergroup_get = zapi.usergroup.get(
    {
        "search":
            {
                "name": "autotest.southbridge.io"
            }
    }
)

if not zbx_usergroup_get:
    print "UserGroup autotest.southbridge.io not found. Test failed"
    raise SystemExit(1)
    
zbx_user_get = zapi.user.get(
    {
        "search":
            {
                "alias": "autotest.southbridge.io"
            }
    }
)

if not zbx_user_get:
    print "User autotest.southbridge.io not found. Test failed"
    raise SystemExit(1)

zbx_maintenance_get = zapi.maintenance.get(
    {
        "search":
            {
                "name": "gitlab-runner_autotest_maintenance"
            }
    }
)

if not zbx_maintenance_get:
    print "gitlab-runner_autotest_maintenance not found. Test failed"
    raise SystemExit(1)
