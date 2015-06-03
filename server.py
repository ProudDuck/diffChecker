#! /usr/bin/python 
# coding=utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import svn_operator
import diff2html
import commands
import time
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class RevisionHandler(tornado.web.RequestHandler):
    def get(self):
        version = self.request.path[1:]
        proj_path = svn_operator.PROJ_PATH_V1 if 'v1' == version else svn_operator.PROJ_PATH_V2

        log_content = svn_operator.run_svn_log_command(proj_path)
        logs = svn_operator.extract_log_object(proj_path, log_content)
        change_lists = svn_operator.each_change_list(logs, proj_path)

	self.render(
	    'revision.html', 
            version=version,
	    change_lists=change_lists
	)

class DiffHandler(tornado.web.RequestHandler):
    def post(self):
        revisions = None
        if (self.request.arguments.has_key('revisions')):
            revisions = self.request.arguments['revisions']

	if revisions == None or len(revisions) != 2:
	    self.write('only support select 2 revisions')   
	    return

	revisions.sort()

        version = self.request.path[1:3]
        proj_path = svn_operator.PROJ_PATH_V1 if 'v1' == version else svn_operator.PROJ_PATH_V2

        log_content = svn_operator.svn_log_r1_r2(proj_path, revisions[0], revisions[1])
        logs = svn_operator.extract_log_object(proj_path, log_content)
        change_lists = svn_operator.each_change_list(logs, proj_path)

	self.render(
	    'revision.html', 
            version=version,
	    change_lists=change_lists
	)

class FileDiffHandler(tornado.web.RequestHandler):
    def post(self):
        file_path = self.get_argument('file_path')
        revision = self.get_argument('revision')

        diff_content = svn_operator.diff_specify_file(file_path, revision)

        diff_html = diff2Html(diff_content)
        self.write(diff_html)

class CompareRevisionsHandler(tornado.web.RequestHandler):
    def get(self):
        version = self.request.path[1:3]
        proj_path = svn_operator.PROJ_PATH_V1 if 'v1' == version else svn_operator.PROJ_PATH_V2

        log_content = svn_operator.run_svn_log_command(proj_path)
        logs = svn_operator.extract_log_object(proj_path, log_content)
        self.render(
            'revisions.html',
            version=version,
            log_objects=logs
        )

def diff2Html(diff_content):
    diff_file_name = 'diff' + str(time.time()) + '.log'
    diff_file = file(diff_file_name, 'w')
    diff_file.write(diff_content)
    diff_file.close()

    command = 'python diff2html.py -i %s -t %d -l %d' %(diff_file_name, 4, 160)
    diff_html = commands.getoutput('python diff2html.py -i ' + diff_file_name + ' -t 4 -l 160')

    os.remove(diff_file_name)

    return diff_html

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
	handlers=[
            (r"/", IndexHandler),
            (r"/v[1-2]", RevisionHandler),
            (r'/v[1-2]/fileDiff', FileDiffHandler),
            (r'/v[1-2]/compareRevisions', CompareRevisionsHandler),
            (r'/v[1-2]/compareRevisions/changes', DiffHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
