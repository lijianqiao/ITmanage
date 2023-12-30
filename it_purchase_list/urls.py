"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: urls.py
 @DateTime: 2023/11/25 0:09
 @Docs: 
"""
from django.urls import path, re_path
from . import views, consumers
from .views import test_view

app_name = 'it_purchase_list'

urlpatterns = [
    path('sunburst-chart/', views.sunburst_chart,
         name='sunburst_chart'),  # 基地部门备件类型分析报表旭日图
    path('rose-chart/', views.rose_chart,
         name='rose_chart'),  # 供应商备件类型总价分析报表南丁格尔玫瑰图
    path('ledger_check/', views.ledger_check_view,
         name='ledger_check'),  # 用于台账核对
    path('logs/', views.logs_admin, name='logs'),   # 日志查询
    path('network_status/', views.network_status,
         name='network_status'),  # 网络状态查询
    path('get_device_status/', views.get_netdevice_status,
         name='get_device_status'),
    path('webssh/',views.jump_webssh,name='webssh'),    # 跳转webssh
    re_path(r'ws/webssh/(?P<ip>[^/]+)/$', consumers.WebSSHConsumer.as_asgi()),
    path('test/', test_view, name='test'),
]
