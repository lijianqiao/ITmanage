"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: celery.py
 @DateTime: 2023/12/5 9:37
 @Docs: 配置Celery
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


# 设置 Django 默认 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITmanage.settings')

# 创建 Celery 实例
app = Celery('ITmanage')

# namespace='CELERY' 作用是允许你在 Django 配置文件中对 Celery 进行配置,但所有 Celery 配置项必须以 CELERY开头，防止冲突
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现并导入任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
