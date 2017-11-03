#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
__author__ = 'vladimirg'
__version__ = '3.0'


import git
import os
import urllib2

def git_check_update(path_to_project):

    # Read information about last local git commit

    zbx_git_HEAD = path_to_project + '/../.git/logs/HEAD'
    g = git.cmd.Git(os.path.dirname(os.path.realpath(__file__)))

    # Fetch information about last remote git commit

    git_resp = urllib2.urlopen("https://gitlab.test.com/scripts/zabbix.commit")
    for line in  open(zbx_git_HEAD) :
    	pass     
    local_commit = line.split(" ")[1] 
    
    # diff local and remote commit number

    if git_resp.read() <>  local_commit :
	print ("Scripts not up to date. Trying update from git")
	git_result = g.pull()
 	print("Scripts was updated from git, need rerun script.")
	return(1)
    else:
	return(0)


