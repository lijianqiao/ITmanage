"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: simpleui_config.py
 @DateTime: 2023/11/28 11:23
 @Docs:  导航栏菜单栏配置
"""

# simpleui配置
# 隐藏首页服务器信息
SIMPLEUI_HOME_INFO = False
# 使用分析，默认开启，统计分析信息只是为了更好的帮助simpleui改进，并不会读取敏感信息。并且分析数据不会分享至任何第三方。
SIMPLEUI_ANALYSIS = False
# 离线模式
SIMPLEUI_STATIC_OFFLINE = True
# 关闭Loading遮罩层，默认开启
# SIMPLEUI_LOADING = False
# 默认主题
SIMPLEUI_DEFAULT_THEME = 'simpleui.css'

SIMPLEUI_CONFIG = {
    'system_keep': False,
    # 'menu_display': ['资产管理', 'IT采购管理', '系统用户权限'],
    'dynamic': False,
    'menus': [
        {
            'app': 'assets',
            'name': '资产管理',
            'icon': 'fa fa-desktop',
            'models': [
                {
                    'name': '资产列表',
                    'icon': 'fa-solid fa-table-list',
                    'url': '/admin/assets/asset/'
                },
                {
                    'name': '维修记录',
                    'icon': 'fa fa-wrench',
                    'url': '/admin/assets/maintenancerecord/'
                },
                {
                    'name': '备件类型',
                    'icon': 'fa fa-tags',
                    'url': '/admin/assets/spareparttype/'
                },
                {
                    'name': '备件',
                    'icon': 'fa-solid fa-screwdriver-wrench',
                    'url': '/admin/assets/sparepart/'
                },
                {
                    'name': '供应商',
                    'icon': 'fa fa-truck',
                    'url': '/admin/assets/supplier/'
                },
                {
                    'name': '基地',
                    'icon': 'fa-solid fa-house-user',
                    'url': '/admin/assets/base/'
                },
                {
                    'name': '部门',
                    'icon': 'fa fa-sitemap',
                    'url': '/admin/assets/department/'
                },
                {
                    'name': '资产管理员',
                    'icon': 'fa fa-user-circle',
                    'url': '/admin/assets/assetmanager/'
                }
            ]
        },
        {
            'app': 'it_purchase_list',
            'name': 'IT采购管理',
            'icon': 'fa fa-shopping-cart',
            'models': [
                {
                    'name': '采购列表',
                    'icon': 'fa fa-list-alt',
                    'url': '/admin/it_purchase_list/purchase/'
                },
                {
                    'name': '供应商',
                    'icon': 'fa-solid fa-truck-field',
                    'url': '/admin/it_purchase_list/supplier/'
                },
                {
                    'name': 'IT台账核对',
                    'icon': 'fa-solid fa-circle-check',
                    'url': '/it_purchase_list/ledger_check/'
                },
                {
                    'name': '网络设备',
                    'icon': 'fa-solid fa-network-wired',
                    'url': '/admin/it_purchase_list/networkdevice/'  # Django admin中网络设备列表的URL名称
                },
                {
                    'name': '网络连接状态',
                    'icon': 'fa-solid fa-network-wired',
                    'url': '/it_purchase_list/network_status/'
                },
                # {
                #     'name': 'webssh',
                #     'icon': 'fa-solid fa-link',
                #     'url': '/admin/it_purchase_list/webssh/'
                # },
            ]
        },
        {
            'app': 'ind_pc',
            'name': '工控机管理',
            'icon': 'fa-solid fa-computer',
            'models': [
                {
                    'name': '工控机信息',
                    'icon': 'fa-solid fa-desktop',
                    'url': '/admin/ind_pc/industrialpc/'
                },
                {
                    'name': '设备类型',
                    'icon': 'fa-solid fa-tape',
                    'url': '/admin/ind_pc/devicetype/'
                },
            ]
        },
        {
            'app': 'office',
            'name': '百宝箱',
            'icon': 'fa-solid fa-toolbox',
            'models': [
                {
                    'name': '工具集',
                    'icon': 'fa-regular fa-file-excel',
                    'url': 'http://10.11.19.14:8051/'
                },
            ]
        },
        {
            'app': 'django_celery_results',
            'name': '周期任务',
            'icon': 'fa-solid fa-square-poll-horizontal',
            'models': [
                {
                    'name': '组结果',
                    'icon': 'fa-solid fa-list-check',
                    'url': '/admin/django_celery_results/groupresult/'
                },
                {
                    'name': '任务结果',
                    'icon': 'fa-solid fa-list-check',
                    'url': '/admin/django_celery_results/taskresult/'
                },
                {
                    'name': '任务结果-flower',
                    'icon': 'fa-solid fa-fan',
                    'url': 'http://10.11.19.14:5555'
                },
                {
                    'name': '周期性任务',
                    'icon': 'fa-solid fa-list-check',
                    'url': '/admin/django_celery_beat/periodictask/'
                },
                {
                    'name': '定时',
                    'icon': 'fa-regular fa-clock',
                    'url': '/admin/django_celery_beat/clockedschedule/'
                },
                {
                    'name': '日程事件',
                    'icon': 'fa-solid fa-calendar-days',
                    'url': '/admin/django_celery_beat/solarschedule/'
                },
                {
                    'name': '计划任务',
                    'icon': 'fa-regular fa-calendar-check',
                    'url': '/admin/django_celery_beat/crontabschedule/'
                },
                {
                    'name': '间隔',
                    'icon': 'fa-solid fa-hourglass-end',
                    'url': '/admin/django_celery_beat/intervalschedule/'
                },
            ]
        },
        {
            'app': 'admin',
            'name': '日志查询',
            'icon': 'fa fa-tag',
            'models': [
                {
                    'name': '日志记录',
                    'icon': 'fa fa-tags',
                    'url': '/admin/auditlog/logentry/'
                },
                {
                    'name': '日志查询',
                    'icon': 'fa-solid fa-book',
                    'url': '/it_purchase_list/logs/'
                },
            ]
        },
        {
            'app': 'auth',
            'name': '系统用户权限',
            'icon': 'fa fa-cog',
            'models': [
                {
                    'name': '管理用户',
                    'icon': 'fa fa-user',
                    'url': '/admin/auth/user/'  # admin后台用户权限
                },
                {
                    'name': '管理用户组',
                    'icon': 'fa fa-users',
                    'url': '/admin/auth/group/'  # admin后台组权限
                },
            ]
        }
    ]
}
