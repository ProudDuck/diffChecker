#! /usr/bin/python 
# coding=utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import svn
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
        proj_path = svn.V1_PATH if 'v1' == version else svn.V2_PATH

        log_content = svn.log(proj_path)
        change_lists = svn.each_change_list(log_content, proj_path)

	self.render(
	    'revision.html', 
            version=version,
	    change_lists=change_lists
	)

class DiffHandler(tornado.web.RequestHandler):
    def post(self):
        revisions = self.request.arguments['revisions'] if self.request.arguments.has_key('revisions') else None

	if revisions == None or len(revisions) != 2:
	    self.write('only support select 2 revisions')   
	    return

	revisions.sort()

        version = self.request.path[1:3]
        proj_path = svn.V1_PATH if 'v1' == version else svn.V2_PATH

        log_content = svn.log_r1_r2(revisions[0], revisions[1], proj_path)
        change_lists = svn.each_change_list(log_content, proj_path)

	self.render(
	    'revision.html', 
            version=version,
	    change_lists=change_lists
	)

class FileDiffHandler(tornado.web.RequestHandler):
    def post(self):
        file_path = self.get_argument('file_path')
        revision = self.get_argument('revision')

        diff_content = svn.file_diff(revision, file_path)

        diff_html = diff2Html(diff_content)
        self.write(diff_html)

class CompareRevisionsHandler(tornado.web.RequestHandler):
    def get(self):
        version = self.request.path[1:3]
        proj_path = svn.V1_PATH if 'v1' == version else svn.V2_PATH

        log_content = svn.log(proj_path)
        logs = [x[0] for x in svn.each_change_list(log_content, proj_path)]
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
    diff_html = commands.getoutput(command)

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
