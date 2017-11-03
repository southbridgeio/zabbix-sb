#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '1.2'


from zabbix_api import ZabbixAPI
import time
import json
import re
import sys
import getpass
import argparse
import os

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

# Connect to server
zapi = ZabbixAPI(zbx_server)
zapi.login(zbx_user,zbx_pass)

parser = argparse.ArgumentParser(description='Arguments to add issue to redmine')
parser.add_argument('--hosts', required=True, action='store', default=None, dest='Hosts', help='Hosts to add in maintenance. To split hosts use , ')
parser.add_argument('--period', required=True, action='store', default=None, dest='Period', help='Period of maintenance. Can use D(day) or H(hourse)')
parser.add_argument('--desc', required=False, action='store', default=None, dest='Desc', help='Description of maintenance period')
args =  parser.parse_args()


## Define variable
zbx_maintenance_hosts = []
zbx_hostname = args.Hosts
zbx_maintenance_duration = args.Period
if args.Desc:
    zbx_maintenance_desc = args.Desc
else:
    zbx_maintenance_desc = " "




active_since = int(time.time())
#Get maintenance in unix time
if re.search('H',zbx_maintenance_duration):
    #active_till = int(re.findall('(\d+)',Period)[0])*3600 + active_since
    maintenance_duration =  int(re.findall('(\d+)',zbx_maintenance_duration)[0])*3600
elif re.search('D',zbx_maintenance_duration):
    #active_till = int(re.findall('(\d+)',Period)[0])*3600*24 + active_since
    maintenance_duration =  int(re.findall('(\d+)',zbx_maintenance_duration)[0])*3600*24
else:
    print ("Wrong format of period")
    exit(1)

## Make connect to zabbix server

zbx_conf_file =os.path.dirname(os.path.realpath(__file__)) + '/../conf/zabbix.conf'

# Get zabbix server connect credentials
zapi = ZabbixAPI(zbx_server)
zapi.login(zbx_user,zbx_pass)

# Get list of exists maintenance
zbx_maintaince = zapi.maintenance.get({"output": "extend",
        "selectGroups": "extend",
        "selectTimeperiods": "extend"})
#Delete old maintenance
for item in zbx_maintaince:
    if int(time.time()) > int(item['active_till']):
        zbx_maintaince = zapi.maintenance.delete([item['maintenanceid']])


## Get list with maintenance hosts
zbx_hostname = zbx_hostname.split(",")

# Generate maintenance name
zbx_maintenance_name = getpass.getuser()+"_"+ zbx_hostname[0].split(".")[1]+"_maintenance"

# Get hosts id
for tmp in zbx_hostname:
    tmp = re.sub("^\s+|\n|\r|\s+$", '',tmp)
    host = zapi.host.get({"output": "extend",
                                "filter": { "name":[tmp]}})
    zbx_maintenance_hosts.append(str(host[0]['hostid']))


## test exists zabbix maintanace plane
zbx_maintaince = zapi.maintenance.get({"output": "extend",
        "selectGroups": "extend",
        "selectTimeperiods": "extend", 
        "filter":{"name":[zbx_maintenance_name]}})

if zbx_maintaince:
    zbx_maintaince = zapi.maintenance.get({"output": "extend", "selectHosts":"extend", "filter": { "name":[zbx_maintenance_name]},
        "selectGroups": "extend",
        "selectTimeperiods": "extend"})
    zbx_maintenanceid = zbx_maintaince[0]['maintenanceid']
    for item in zbx_maintaince[0]['hosts']:
        if item['hostid'] not in zbx_maintenance_hosts:
            zbx_maintenance_hosts.append(item['hostid'])
    zbx_maintaince = zapi.maintenance.update({"description":zbx_maintenance_desc,
                                          'maintenanceid': zbx_maintenanceid,
                                          "active_since":active_since,
                                          "active_till":maintenance_duration + active_since ,
                                          "hostids":json.loads(json.dumps(zbx_maintenance_hosts)),
                                          "timeperiods":[
                                                {       "start_date":active_since,
                                                        "period":maintenance_duration
                                                } ]
    })
    if zbx_maintaince:
        print ("Maintenance period update   [Ok]")
else:
    zbx_maintaince = zapi.maintenance.create({"description":zbx_maintenance_desc,
                                          "name":zbx_maintenance_name,
                                          "active_since":active_since,
                                          "active_till":maintenance_duration + active_since ,
                                          "hostids":json.loads(json.dumps(zbx_maintenance_hosts)),
                                          "timeperiods":[
                                              { "period":maintenance_duration} ]
    })
    if zbx_maintaince:
        print ("Maintenance period create  [Ok]")
