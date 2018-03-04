#!/usr/bin/env python 
#encoding=utf-8
import json

from sqlalchemy import and_

from api_request import post_http
from db.models import db_session, Orders, ConsumeLog, RechargeLog, Invoice, UploadLog
from etc.conf import *
from sync_realauth import WorderDBSync
from utils import Utils


class DBSync(object):
    @staticmethod
    def send_order_to_cmdb(id=None):
        orders = Orders.query.filter().all()
        db_session.close()
        if not orders:
            print "can not found any orders...."
            return False
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for order in orders:
            data = {"type": "order",
                    "uuid": order.uid,
                    "property": {"user_name": order.user_name,
                                 "project_name": order.project_name,
                                 "start_time": Utils.cover_time2str(order.start_time),
                                 "end_time": Utils.cover_time2str(order.end_time),
                                 "type": (u"立即结算" if order.order_type == 1 else u"预付费"),
                                 "status": (u"计费中" if not order.status else u"已结算"),
                                 "resource_name": order.resource_name,
                                 #"resource_type": order.resource_type,
                                 "used": order.used,
                                 "discount": order.off,
                                 }
                    }
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db. uuid: <{0}>".format(order.uid)
                print em
            print ret.json()

    @staticmethod
    def send_consume_log(id=None):
        if id:
            # consumes = ConsumeLog.query.filter(and_(ConsumeLog.money > 0,
            #                                         ConsumeLog.uid == id)).all()
            consumes = ConsumeLog.query.filter(and_(ConsumeLog.uid == id)).all()
        else:
            consumes = ConsumeLog.query.filter(ConsumeLog.money > 0).all()
        db_session.close()
        if not consumes:
            print "can not found any consumes...."
            return False
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for consume in consumes:
            # 查找与该条消费记录相关的订单记录
            remark = ""
            if consume.order_uid:
                order = Orders.query.filter(Orders.uid == consume.order_uid).first()
                if order:
                    remark = u"资源名：{0},使用量：{1},使用时长（分）：{2}".format(order.resource_name,
                                                                      order.used,
                                                                      (order.end_time - order.start_time) / 60.0)

            data = {"type": "consume",
                    "uuid": consume.uid,
                    "property": {"user_name": consume.user_name,
                                 "project_name": consume.user_name,
                                 "money": float(consume.money),
                                 "time": Utils.cover_time2str(consume.log_time),
                                 "remark": remark,
                                 "details": consume.details
                                 }
                    }
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db. uuid: <{0}>".format(consume.uid)
                print em
            print ret.json()

    @staticmethod
    def send_recharge_log(id=None):
        if id:
            r_logs = RechargeLog.query.filter(and_(RechargeLog.recharge_way != "deveops",
                                                   RechargeLog.trade_status == "success",
                                                   RechargeLog.uid == id)).all()
        else:
            r_logs = RechargeLog.query.filter(and_(RechargeLog.recharge_way != "deveops",
                                                   RechargeLog.trade_status == "success")).all()
        db_session.close()
        if not r_logs:
            print "can not found any recharge log...."
            return False
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for r_log in r_logs:
            r_type = ""
            if r_log.recharge_way == "Alipay":
                r_type = u"支付宝"
            if r_log.recharge_way == "deveops":
                r_type = u"测试虚冲"
            if r_log.recharge_way == "discount_id":
                r_type = u"优惠卷"
            if r_log.recharge_way == "unionpay":
                r_type = u"银行转账"

            data = {"type": "recharge",
                    "uuid": r_log.uid,
                    "property": {"user_name": r_log.user_name,
                                 "project_name": r_log.user_name,
                                 "type": r_type,
                                 "money": float(r_log.money),
                                 "time": Utils.cover_time2str(r_log.log_time),
                                 "status": u"成功",
                                 "remark": u"{0}".format(("" if not r_log.description else u"描述： " + r_log.description)),
                                 "is_invoiced": (u"已开" if r_log.is_invoiced else u"未开")
                                 }
                    }
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db. uuid: <{0}>".format(r_log.uid)
                print em
            print ret.json()

    @staticmethod
    def send_invoice(id=None):
        invoices = Invoice.query.filter(and_(Invoice.deleted == False)).all()
        db_session.close()
        if not invoices:
            print "can not found any invoices...."
            return False
        admin_token = Utils.get_token()
        if not admin_token[0]:
            print "get admin token error...."
            return False
        url = cmdb_ep + "/assets"
        headers = {'X-Auth-Token': admin_token[1].strip(), 'Content-type': 'application/json'}
        for invoice in invoices:
            # 查找用户上传的文件记录
            upload_obj = UploadLog.query.filter(UploadLog.uuid == invoice.upfile_uuid).first()
            if not upload_obj:
                pass
            data = {"type": "invoice",
                    "uuid": invoice.uuid,
                    "property": {"logistics_no": invoice.logistics_no,
                                 "logistics_company": invoice.logistics_company,
                                 "title": invoice.title,
                                 "status": invoice.status,
                                 "post_address": invoice.post_address,
                                 "post_user": invoice.post_user,
                                 "post_phone": invoice.post_phone,
                                 "money": float(invoice.money),
                                 "invoice_no": invoice.invoice_no,
                                 "title_type": invoice.title_type,
                                 "title_mode": invoice.title_mode,
                                 "context": invoice.context,
                                 "corporation_name": invoice.corporation_name,
                                 "taxpayer_dentity": invoice.taxpayer_dentity,
                                 "register_address": invoice.register_address,
                                 "register_phone": invoice.register_phone,
                                 "deposit_bank": invoice.deposit_bank,
                                 "deposit_account": invoice.deposit_account,
                                 "user_name": invoice.user_name,
                                 "application_date": invoice.application_date,
                                 "complete_date": invoice.complete_date,
                                 "description": invoice.description,
                                 "recharge_uuids": invoice.recharge_uuids,
                                 "deleted": invoice.deleted,
                                 "yezz_url": (upload_obj.yezz_url if upload_obj else None),
                                 "swdj_url": (upload_obj.swdj_url if upload_obj else None),
                                 "yhkh_url": (upload_obj.yhkh_url if upload_obj else None)
                                 }
                    }
            data = json.dumps(data)
            ret = post_http(url=url, data=data, headers=headers)
            if ret.status_code != 200:
                em = "error with sync db.invoice  uuid: <{0}>".format(invoice.uuid)

