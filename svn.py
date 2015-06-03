#! /usr/bin/python
# coding=utf-8

import commands
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

REPO = 'svn://192.168.58.211/B2C'
PROJ_PATH_V1 = '/90source/trunk'
PROJ_PATH_V2 = '/90source/2.0/trunk'

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
    output = unicode(commands.getoutput(log_command), 'utf-8')
    
    change_list = re.compile(r'[AMD] \/.*').findall(output)
    return change_list

def svn_log_r1_r2(proj_path, r1, r2):
    log_command = 'svn log %s -r %s:%s -v' %(REPO + proj_path, r1, r2)
    return unicode(commands.getoutput(log_command), 'utf-8')

def run_svn_log_command(proj_path):
    log_limit = 100

    log_command = 'svn log %s --limit %d' %(REPO + proj_path, log_limit)
    return unicode(commands.getoutput(log_command), 'utf-8')

def run_svn_diff_command(r1, r2, proj_path):
    log_command = 'svn diff %s -r %s:%s' %(REPO + proj_path, r1, r2)

    return commands.getoutput(log_command)
    
def diff_specify_file(file_path, revision):
    log_command = 'svn diff -c %s %s' %(revision, REPO + file_path[2:])
    return commands.getoutput(log_command)

def extract_log_object(proj_path, log_content):
    log_objects = []
    for log in log_content.split('-' * 72):
        if log != None:
	    ss = log.split('|')
	    if len(ss) == 4:
   		revision = ss[0].strip()
		author = ss[1].strip()
		date = ss[2].strip()[0:19]
		comment = ss[3].strip()
		comment = (comment.split('\n')[len(comment.split('\n')) - 1] if len(comment.split('\n')) > 1  else '')

		log_object = Log(revision, author, date, comment)
		log_objects.append(log_object)

    return log_objects

def each_change_list(log_objects, proj_path):
    map = dict()
    for log_object in log_objects:
        change_list = run_svn_revision_log_command(log_object.revision, proj_path)
        map[log_object] = change_list

    map = sorted(map.iteritems(), key=lambda d:d[0].revision, reverse=True)
    return map

if __name__ == '__main__':
    pass
