"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: task.py
 @DateTime: 2023/12/6 11:57
 @Docs:  创建一个Celery任务来执行网络设备的状态检查
"""
from celery import shared_task
from django.core.cache import cache
from .models import NetworkDevice
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity


@shared_task
def check_network_devices_status():
    devices = NetworkDevice.objects.all()
    for device in devices:
        status = get_device_status(device.ip_address)
        # 缓存状态300秒
        cache.set(f'network_device_status_{device.pk}', status, timeout=300)


def get_device_status(ip_address):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData('oppein@11', mpModel=1),
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))  # 获取系统描述
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"SNMP Error: {ip_address} {errorIndication}")
        return '不在线或无法访问'
    elif errorStatus:
        print(
            f"SNMP Error Status: {ip_address} {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
        return '不在线或无法访问'
    else:
        # 可以从varBinds获取更多信息，这里我们只是检查是否有响应
        return '在线'
