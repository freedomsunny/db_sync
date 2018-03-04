#!/usr/bin/env python 
#encoding=utf-8
import json

from sqlalchemy import and_

from api_request import post_http
from db.models_worder import db_session, Worder, APPService
from etc.conf import *
from utils import Utils


class WorderDBSync(object):
    @staticmethod
    def send_worder_to_cmdb():
        worders = Worder.query.filter(and_(Worder.title == u"实名认证",
                                           Worder.status == True)).all()
        db_session.close()
        if not worders:
            print "can not found any orders...."
            return False
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for worder in worders:
            # 获取实名认证类型
            app_obj = APPService.query.filter(APPService.id == worder.app_service_id).first()
            auth_type = app_obj.name
            data = {"type": "realauth",
                    "uuid": worder.id,
                    "property": {"user_name": worder.user_name,
                                 "created_at": str(worder.created_at),
                                 "auth_id": worder.auth_id,
                                 "auth_phone": worder.auth_phone,
                                 "auth_name": worder.auth_name,
                                 "card": "",
                                 "auth_type": auth_type,
                                 "status": u"通过"
                                 }
                    }
            print data
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db. uuid: <{0}>".format(worder.id)
                print em
            print ret.json()

