"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: wechatbot.py
 @DateTime: 2023/12/26 17:15
 @Docs:
"""
import ipaddress

import requests


class WechatWorkBot:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message, mentioned_list=None, mentioned_mobile_list=None):
        payload = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_list": mentioned_list if mentioned_list else [],
                "mentioned_mobile_list": mentioned_mobile_list if mentioned_mobile_list else []

            }
        }
        response = requests.post(self.webhook_url, json=payload)
        return response


def determine_notification_details(device_ip, status, rack_position):
    if status != '未知':
        return None, None, None

    # B栋汇聚
    if device_ip == ipaddress.ip_address('10.11.210.202'):
        # 只通知默认联系人和所有人
        message = f"IP为{device_ip}的厂区汇聚交换机掉线，位置{rack_position}，厂区全部断网，正在处理，请稍等。。。"
        return ["@all"], [], message
    # A栋汇聚
    elif device_ip == ipaddress.ip_address('10.11.210.201'):
        message = f"IP为{device_ip}的汇聚交换机掉线，导致厂区A栋全部断网，请检查{rack_position}电源是否正常。"
        # 只通知默认联系人和所有人
        return [], ['13160579654'], message
    # C栋汇聚
    elif device_ip == ipaddress.ip_address('10.11.210.203'):
        message = f"IP为{device_ip}的汇聚交换机掉线，导致厂区C栋3楼全部断网，请检查{rack_position}电源是否正常。"
        # 只通知默认联系人和所有人
        return [], ['13808250220'], message
    # E栋汇聚
    elif device_ip == ipaddress.ip_address('10.11.210.205'):
        message = f"IP为{device_ip}的汇聚交换机掉线，导致厂区E栋全部断网，请检查{rack_position}电源是否正常。"
        # 只通知默认联系人和所有人
        return [], ['13808250220'], message
    # F栋汇聚
    elif device_ip == ipaddress.ip_address('10.11.210.206'):
        message = f"IP为{device_ip}的汇聚交换机掉线，导致厂区F栋全部断网，请检查{rack_position}电源是否正常。"
        # 只通知默认联系人和所有人
        return [], ['18780178737'], message
    # G栋汇聚
    elif device_ip == ipaddress.ip_address('10.11.210.207'):
        message = f"IP为{device_ip}的汇聚交换机掉线，导致厂区G栋全部断网，请检查{rack_position}电源是否正常。"
        # 只通知默认联系人和所有人
        return [], ['17781561096'], message

    # 定义 IP 范围和对应的通知细节
    ip_ranges = {
        # A栋1L
        ('10.11.210.1', '10.11.210.2', '10.11.210.3', '10.11.210.4', '10.11.210.82', '10.11.90.126'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["13360035347","19908028400",'18381022140']
        },
        # A栋2L
        ('10.11.210.5', '10.11.210.6', '10.11.210.7', '10.11.210.8'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["19960319266","18382764980",'18111648212','13160579654']
        },
        # A栋3L
        ('10.11.210.9', '10.11.210.10', '10.11.210.11', '10.11.210.12'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["15918527387","15181417440",'18020081973','18328508672']
        },
        # B栋1L
        ('10.11.210.13', '10.11.210.14', '10.11.210.15', '10.11.210.16', '10.11.210.73',
         '10.11.210.86','10.11.210.72', '10.11.91.191'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["15975377167","15884697366",'13666137446','13527781856','18380448309']
        },
        # B栋2L
        ('10.11.210.17', '10.11.210.19', '10.11.210.20', '10.11.210.90', '10.11.210.43',
         '10.11.210.84', '10.11.210.91', '10.11.210.64'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["15918527387","15181417440",'18328508672','13540671406']
        },
        # B栋3L
        ('10.11.210.77', '10.11.210.74', '10.11.210.92', '10.11.210.83', '10.11.210.23', '10.11.210.24'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["18512881261","18011982935",'15883329165',
                                      '15215167161','18880455340','15108249213','18284571708']
        },
        # C栋3L
        ('10.11.210.78', '10.11.210.79', '10.11.210.80', '10.11.210.81', '10.11.210.93', '10.11.210.21'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["15992490622",'13808250220']
        },
        # E栋1L
        ('10.11.210.56', '10.11.210.57'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["18227755889", '18180099399']
        },
        # E栋2L
        ('10.11.210.58', '10.11.210.59'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["13808250220",'13649057662']
        },
        ('10.11.210.66', '10.11.210.70'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["18328510546"]
        },
        # F栋1L
        ('10.11.210.67', '10.11.210.32', '10.11.210.33', '10.11.210.34'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["18780178737"]
        },
        ('10.11.210.18',): {
            "mentioned_list": [],
            "mentioned_mobile_list":["13882043113"]
        },
        # F栋2L
        ('10.11.210.68',): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["13608093991"]
        },
        # F栋3L
        ('10.11.210.76',): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["18283528013"]
        },
        # G栋1L
        ('10.11.210.25', '10.11.210.26', '10.11.210.27'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["17781561096"]
        },
        # G栋2L
        ('10.11.210.28', '10.11.210.29', '10.11.210.31'): {
            "mentioned_list": [],
            "mentioned_mobile_list": ["17781561096"]
        },
    }

    for ip_range, notification_details in ip_ranges.items():
        if device_ip in (ipaddress.ip_address(ip) for ip in ip_range):
            mentioned_list = notification_details.get("mentioned_list", [])
            mentioned_mobile_list = notification_details.get("mentioned_mobile_list", [])
            custom_message = f"IP为{device_ip}的交换机掉线了，请检查{rack_position}的电源供电是否正常。"
            return mentioned_list, mentioned_mobile_list, custom_message

    # 默认联系人，当没有匹配的条件时使用
    default_mentioned_mobile_list = ["13684404523", '18381022140']
    default_message = f"请检查{device_ip}设备是否正常，位于{rack_position}。"

    return [], default_mentioned_mobile_list, default_message
