@echo off
cd /d D:\ITmanage
REM 切换anaconda环境
call activate anq
ping -n 1 127.0.0.1 >nul
REM 获取当前日期
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do (
    set day=%%c
    set month=%%b
    set year=%%a
)

REM 生成日志文件名
set log_file_name=celery_flower_%year%_%month%_%day%.log

REM 运行worker
celery -A ITmanage flower --address=10.11.19.12 --port=5555 --basic_auth=admin:123 >> D:\ITmanage\logs\%log_file_name% 2>&1
