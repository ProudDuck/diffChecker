#! /usr/bin/python
# coding=utf-8

import commands
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

REPO = 'svn://192.168.58.211/B2C'
V1_PATH = '/90source/trunk'
V2_PATH = '/90source/2.0/trunk'

class Log():
    def __init__(self, revision, author, date, comment):
	self.revision = revision
	self.author = author
	self.date = date
	self.comment = comment
   
    def __str__(self):
	return ' '.join([self.revision, self.date, self.author, self.comment])
	

def run_svn_revision_log_command(revision, proj_path):
    log_command = 'svn log %s -r %s -v' %(REPO + proj_path, revision)
    output = commands.getoutput(log_command)
    
    change_list = re.compile(r'[AMD] \/.*').findall(output)
    return change_list

def log_r1_r2(r1, r2, proj_path):
    '''
        log between 2 revisions
    '''

    log_command = 'svn log %s -r %s:%s -v' %(REPO + proj_path, r1, r2)
    return commands.getoutput(log_command)

def log(proj_path):
    '''
        100 logs to HEAD
    '''

    log_limit = 100

    log_command = 'svn log %s --limit %d -v' %(REPO + proj_path, log_limit)
    return commands.getoutput(log_command)

def diff(r1, r2, proj_path):
    '''
        diff between 2 revisions of all changed files
    '''

    log_command = 'svn diff %s -r %s:%s' %(REPO + proj_path, r1, r2)

    return commands.getoutput(log_command)
    
def file_diff(revision, file_path):
    '''
       diff between 2 revisions of one single file
    '''

    log_command = 'svn diff -c %s %s' %(revision, REPO + file_path[2:])
    return commands.getoutput(log_command)

def each_change_list(log_content, proj_path):
    '''
        extract log object and its changed file list from log_content
    '''

    change_lists = dict()
    
    for log in log_content.split('-' * 72):
        if log is not None:
            attrs = log.split('|')
            if len(attrs) == 4:
                revision = attrs[0].strip()
		author = attrs[1].strip()
		date = attrs[2].strip()[0:19]
		comment = re.split(r'[AMD] \/.*', attrs[3].strip())[-1]

                change_lists[Log(revision, author, date, comment)] = re.compile(r'[AMD] \/.*').findall(log)

    return sorted(change_lists.iteritems(), key=lambda d:d[0].revision, reverse=True)

if __name__ == '__main__':
    pass
