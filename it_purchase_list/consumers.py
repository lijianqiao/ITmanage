"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: consumers.py
 @DateTime: 2023/12/11 11:14
 @Docs:  定义一个 WebSocket 消费者
"""
import paramiko
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json


class WebSSHConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.channel = None
        self.ssh = None

    async def connect(self):
        await self.accept()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    async def disconnect(self, close_code):
        if self.channel:
            self.channel.close()
        if self.ssh:
            self.ssh.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                # 尝试将文本数据解析为 JSON
                data = json.loads(text_data)
                # 处理连接命令
                await self.handle_json_data(data)
            except json.JSONDecodeError:
                # 处理普通的 shell 输入
                await self.handle_shell_input(text_data)

    async def handle_json_data(self, data):
        # 处理连接命令
        command = data.get('command')
        if command == 'connect':
            username = data.get('username', 'opcdjr')
            password = data.get('password')
            ip_address = data.get('ip_address')
            port = data.get('port', 22)  # 默认端口为 22
            await self.connect_ssh(ip_address, port, username, password)

    async def handle_shell_input(self, text_data):
        # 如果 SSH 通道已经打开，则发送数据
        if self.channel:
            self.channel.send(text_data)
            await self.send_data()

    async def connect_ssh(self, ip_address, port, username, password):
        try:
            self.ssh.connect(ip_address, port=int(port), username=username, password=password)
            self.channel = self.ssh.invoke_shell()
            await self.send_data()
        except Exception as e:
            await self.send(text_data=str(e))
            await self.close()


    async def send_data(self):
        try:
            # 检查是否有数据可以接收
            while self.channel.recv_ready():
                data = self.channel.recv(1024).decode('utf-8')
                if data:
                    await self.send(text_data=data)
                await asyncio.sleep(0.01)  # 让出控制权给事件循环
        except Exception as e:
            await self.send(text_data=str(e))
