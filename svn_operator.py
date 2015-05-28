#! /usr/bin/python
# coding=utf-8

import commands
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Svn_Log():
    def __init__(self, revision, author, date, comment):
	self.revision = revision
	self.author = author
	self.date = date
	self.comment = comment
   
    def __str__(self):
	return ' '.join([self.revision, self.author, self.comment, self.date])
	

def run_svn_log_command():
    repo = 'svn://192.168.58.211/B2C/90source/trunk'
    log_limit = 100

    log_command = 'svn log ' + repo + ' --limit ' + str(log_limit)

    return unicode(commands.getoutput(log_command), 'utf-8')

def run_svn_diff_command(r1, r2):
    repo = 'svn://192.168.58.211/B2C/90source/trunk'

    log_command = 'svn diff ' + repo + ' -r ' + r1 + ':' + r2

    #return unicode(commands.getoutput(log_command), 'utf-8')
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

		log_object = Svn_Log(revision, author, date, comment)
		log_objects.append(log_object)

    return log_objects

if __name__ == '__main__':
    t =  run_svn_diff_command('r7806', 'r7807')
    f = file('hah.html', 'w')
    f.write(t)
    f.close()
