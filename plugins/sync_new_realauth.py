#encoding=utf-8
import sys
sys.path.append("/root/db_sync")
from etc.conf import *
from db.models_sia import db_session, Images, AuthInfo
from utils import Utils
from api_request import post_http


from sqlalchemy import and_
import json


def get_pictuer_url(file_name):
    return 'http://{0}:{1}/picture/{2}'.format(floting_ip, sia_port, file_name.strip())


class NewRealAuth(object):
    @staticmethod
    def sync_new_realauth(id=None):
        result = []
        if id:
            auth_infos = AuthInfo.query.filter(and_(AuthInfo.deleted == False,
                                                    AuthInfo.id == id,
                                                    )).all()
        else:
            auth_infos = AuthInfo.query.filter(AuthInfo.deleted == False,).all()
        if not auth_infos:
            print "can not found any real name auth...."
            return {}
        for auth_info in auth_infos:
            images = Images.query.filter(and_(Images.deleted == False,
                                              Images.auth_info_id == auth_info.id)).all()
            auth_info.image_list = []
            for image in images:
                auth_info.image_list.append(get_pictuer_url(image.name))
            result.append(auth_info)
        db_session.close()
        # 同步到cmdb
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for auth_info in result:
            data = {"type": "new_realauth",
                    "uuid": auth_info.id,
                    "property": {"user_name": auth_info.user_name,
                                 "bank_branch_name": auth_info.bank_branch_name,
                                 "status": int(auth_info.status),
                                 "bank_address": auth_info.bank_address,
                                 "images": auth_info.image_list,
                                 "bank_area": auth_info.bank_area,
                                 "bank_id": auth_info.bank_id,
                                 "bank_name": auth_info.bank_name,
                                 "auth_money": float(auth_info.auth_money),
                                 "created_at": str(auth_info.created_at),
                                 "auth_name": auth_info.auth_name,
                                 "auth_id": auth_info.auth_id,
                                 "auth_phone": auth_info.auth_phone,
                                 "auth_type": auth_info.auth_type
                                 }
                    }
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db. uuid: <{0}>".format(auth_info.uid)
                print em
            print ret.json()


if __name__ == '__main__':
    NewRealAuth.sync_new_realauth()