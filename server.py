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
	self.render(
	    "index.html", 
	    log_objects=svn_operator.extract_log_object()
	)

class DiffHandler(tornado.web.RequestHandler):
    def post(self):
	revisions = self.request.arguments['revisions']
	if revisions == None or len(revisions) != 2:
	    self.write('only support select 2 revisions')   
	    return

	revisions.sort()

	diff_content = svn_operator.run_svn_diff_command(revisions[0], revisions[1])

	diff_file_name = 'diff' + str(time.time()) + '.log'
        diff_file = file(diff_file_name, 'w')
	diff_file.write(diff_content)
	diff_file.close()

	diff_html = commands.getoutput('cat ' + diff_file_name + ' | python diff2html.py')
	html_file_name = 'diff' + str(time.time()) + '.html'
	html_file = file(html_file_name, 'w')
	html_file.write(diff_html)
	html_file.close()

        self.render(html_file_name)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
	handlers=[(r"/", IndexHandler), (r'/diff', DiffHandler)],
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
