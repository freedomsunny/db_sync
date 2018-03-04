#encoding=utf-8
import sys
sys.path.append("/root/db_sync")
import json
import tornado.web
from tornado.netutil import bind_sockets

from plugins.sync_charging import DBSync
from plugins.sync_new_realauth import NewRealAuth


class Base(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(Base, self).__init__(application, request, **kwargs)
        if request.method != 'OPTIONS':
            self.context = {'start': int(self.get_argument("start", 0)),
                            'length': int(self.get_argument("length", 10000))}

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        self.set_header("Access-Control-Allow-Headers", "X-Auth-Token, Content-type")
        self.set_header("Content-Type", "application/json")
        self.set_header("Content-Type", "application/vnd.apple.mpegurl")

    def options(self, *args, **kwargs):
        self.finish()


class SyncData(Base):
    def put(self, **kwargs):
        """
        API用于接收实时数据，同步到cmdb
        resource_id: 单条资源唯一ID
        resource_type: 资源类型
        :return:
        """
        data = json.loads(self.request.body)
        resource_id = str(self.path_kwargs.get('rid', "")).strip()
        resource_type = data.get("resource_type")
        print "resource_type====", resource_type
        print "resource_id====", resource_id
        if resource_type == "recharge":
            DBSync.send_recharge_log(id=resource_id)
        if resource_type == "consume":
            DBSync.send_consume_log(id=resource_id)
        if resource_type == "new_realauth":
            NewRealAuth.sync_new_realauth(id=resource_id)

        # resource_type = self.get_argument("resource_type", "")


application = tornado.web.Application([
    (r"/sync/(?P<rid>.+)$", SyncData),
    ])

if __name__ == "__main__":
    sockets = bind_sockets(8888, "0.0.0.0")
    tornado.process.fork_processes(0)
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()

