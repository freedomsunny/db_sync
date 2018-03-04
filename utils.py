#!/usr/bin/env pyton

import json
import time
import psutil

from api_request import post_http
from etc.conf import *


class Utils(object):
    @staticmethod
    def get_token(username=username, password=password, tenant=tenant):
        if tenant:
            data = {"auth":
                        {"passwordCredentials":
                             {"username": username,
                              "password": password},
                         'tenantName': tenant
                         },
                    }
            r = post_http(method='post', url='%s/tokens' % keystone_admin_endpoint,
                          data=json.dumps(data))
            if r.status_code == 200 and r.json().get('access', ''):
                token = r.json().get('access').get("token").get("id")
                return True, token
            else:
                return False, 500

    @staticmethod
    def cover_time2str(times_tamp):
        if not times_tamp:
            return ""

        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(times_tamp)))

    @staticmethod
    def order_used_money(order, price, immed=False):
        """
        this method to expr how much used by a order(every minute money.is a single order)
        :param order: order db object
        :param price: price db object
        immed : order type is the immed pay
        :return: float: money use
            """
        try:
            # get order about
            order_info = GeTOrderAboutFromDB(order, price)
            # get order's off  add by huangyingjun 2017/08/4
            order_off = 1
            if order.off is not None:
                order_off = float(order.off)
            # if immed expr order total used money. else expr every minute money
            if immed:
                order_money = order_info.used_minute * (float(order_info.order_used) / order_info.price_unit * (
                    (float(order_info.price_price) / (order_info.price_time * 60)) * order_off))
            else:
                order_money = (float(order_info.order_used) / order_info.price_unit) * (
                    (float(order_info.price_price) / (order_info.price_time * 60)) * order_off)
            return order_money
        except Exception as e:
            em = "expr order failed. msg: {0}".format(e)
            print em
            return False


class GeTOrderAboutFromDB(object):
    def __init__(self, order, price):
        """
        method to parser order and price info from db
        :param order: order db object
        :param price: price db object
        """
        if not order.used or not float(order.used):
            em = "resource is not used. resource id: <{0}>. resource name :<{1}>".format(order.resource_id,
                                                                                         price.name)
            print em
            raise ValueError(em)
        if not price.unit or not float(price.unit):
            em = "price.unit is not define. price type: <{0}>".format(price.price_type)
            print em
            raise ValueError(em)
        if not price.price or not float(price.price):
            em = "price.price is not define. price type: <{0}>".format(price.price_type)
            print em
            raise ValueError(em)
        if not price.time or not float(price.time):
            em = "price.time is not define. price type: <{0}>".format(price.price_type)
            print em
            raise ValueError(em)
        if order.end_time and order.start_time:
            if int(order.end_time) <= int(order.start_time):
                em = "order's end_time can not be le start_time. resource id: <{0}>".format(order.resource_id)
                print em
                raise ValueError(em)
        self.order_used = order.used
        self.price_unit = price.unit
        self.price_price = price.price
        self.price_time = price.time
        self.start_time = order.start_time
        self.end_time = order.end_time
        if order.order_type == 1 and self.end_time:
            self.used_minute = float((self.end_time - self.start_time) / 60)
        else:
            self.used_minute = 1


def find_procs_by_name(name):
    """Return a list of processes matching 'pid'."""
    result = []
    for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
        for cmd in p.info["cmdline"]:
            if name in cmd:
                result.append(p.pid)
    return result
