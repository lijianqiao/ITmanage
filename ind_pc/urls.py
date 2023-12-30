"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: urls.py
 @DateTime: 2023/12/14 15:48
 @Docs: 工控机管理应用路由
"""
from django.urls import path, re_path
from . import views

app_name = 'ind_pc'

urlpatterns = [
    path('industrial_pc_stats/', views.industrial_pc_stats, name='industrial_pc_stats'), # 绘制工控机信息图表
]
