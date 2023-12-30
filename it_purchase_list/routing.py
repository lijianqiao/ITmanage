"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: routing.py
 @DateTime: 2023/12/11 11:13
 @Docs:  定义路由
"""
from django.urls import path, re_path
from it_purchase_list import consumers

websocket_urlpatterns = [
    path('ws/webssh/<str:ip_address>/', consumers.WebSSHConsumer.as_asgi()),
]
