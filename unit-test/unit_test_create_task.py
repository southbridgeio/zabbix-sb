#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '3.0'

from redminelib import Redmine
import time
import os
import re
import datetime

def create(redmine_tag, redmine_priority, ProjectID,
                        issue_Subject, issue_Body):


    # Define vars

    Admin_ID = 76

    # Define connect to redmine
    # Defining constants
    redmine_conf_file = os.path.dirname(os.path.realpath(__file__)) + '/../conf/redmine.conf'

    # Get redmine server connect credentials
    for tmp_line in open(redmine_conf_file):
        if "server" in tmp_line: redmine_server = str(tmp_line.split("=")[1]).rstrip()
        if "key" in tmp_line: redmine_key = str(tmp_line.split("=")[1]).rstrip()

    # Connect to redmine server
    redmine = Redmine(redmine_server, key=redmine_key)

    # Search already created issue
    issueExist = redmine.issue.filter(
        project_id=ProjectID.strip(),
        subject=issue_Subject
    )
    i = 0
    while i < 5:
        try:
            if not issueExist:
                print(time.strftime('%Y-%m-%d %H:%M:%S') + ' Create issue: ' + issue_Subject)
                issue = redmine.issue.create(
                    project_id=ProjectID.strip(),
                    subject=issue_Subject,
                    tracker_id=3,
                    description=issue_Body,
                    status_id=1,
                    tag_list='zabbix, ' + redmine_tag,
                    priority_id=redmine_priority,
                    assigned_to_id=Admin_ID
                )
            else:
                # If issue created, add comment
                print(time.strftime('%Y-%m-%d %H:%M:%S') + ' Update issue: ' + issue_Subject)
                issue = redmine.issue.update(
                    issueExist[0].id,
                    notes=issue_Body
                )
        # Error processing
        except Exception as e:
            print("Can't access to factory, wait 3 minute")
            print(e)
            time.sleep(36)
            i = i + 1
        else:
            i = 10
    # Finally send return code
    if i != 10:
        return 1
    else:
        return 0
        
ProjectID = 'operation'
issue_Subject = "Zabbix: автотест скрипта не пройден!! " + \
                    datetime.datetime.now().strftime("%d.%m.%Y") + '.'
issue_Body = 'https://gitlab.test.com/scripts/zabbix/pipelines'
redmine_tag = 'zabbix, порядок'
redmine_priority = '5'

# Create issue in redmine
result = create(redmine_tag, redmine_priority, ProjectID,
                        issue_Subject, issue_Body)

