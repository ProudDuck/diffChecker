#! /usr/bin/python
# coding=utf-8

import commands
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

REPO = 'svn://192.168.58.211/B2C/90source/trunk'

class SVN_Log():
    def __init__(self, revision, author, date, comment):
	self.revision = revision
	self.author = author
	self.date = date
	self.comment = comment
   
    def __str__(self):
	return ' '.join([self.revision, self.date, self.author, self.comment])
	

def run_svn_revision_log_command(revision):
    log_command = 'svn log %s -r %s -v' %(REPO, revision)
    output = unicode(commands.getoutput(log_command), 'utf-8')
    
    change_list = re.compile(r'[AMD] \/.*').findall(output)
    return change_list

def run_svn_log_command():
    log_limit = 100

    log_command = 'svn log %s --limit %d' %(REPO, log_limit)
    return unicode(commands.getoutput(log_command), 'utf-8')

def run_svn_diff_command(r1, r2):
    log_command = 'svn diff %s -r %s:%s' %(REPO, r1, r2)

    return commands.getoutput(log_command)
    
def diff_specify_file(file_path, revision):
    repo = 'svn://192.168.58.211/B2C'
    
    log_command = 'svn diff -c %s %s' %(revision, repo + file_path[2:])
    return commands.getoutput(log_command)

def extract_log_object():
    log_content = run_svn_log_command()
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

		log_object = SVN_Log(revision, author, date, comment)
		log_objects.append(log_object)

    return log_objects

def each_change_list(log_objects):
    map = dict()
    for log_object in log_objects:
        change_list = run_svn_revision_log_command(log_object.revision)
        map[log_object] = change_list

    map = sorted(map.iteritems(), key=lambda d:d[0].revision, reverse=True)
    return map

if __name__ == '__main__':
    #t =  run_svn_diff_command('r7806', 'r7807')
    #run_svn_revision_log_command('r7806')
    change_lists = each_change_list(extract_log_object())
    for c in change_lists:
        print c[1]
