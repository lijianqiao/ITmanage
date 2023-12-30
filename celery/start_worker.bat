@echo off
cd /d D:\ITmanage
call activate anq
ping -n 1 127.0.0.1 >nul
REM 获取当前日期
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do (
    set day=%%c
    set month=%%b
    set year=%%a
)

REM 生成日志文件名
set log_file_name=celery_worker_%year%_%month%_%day%.log

REM 运行worker
celery -A ITmanage worker -l info -P eventlet --logfile=D:\ITmanage\logs\%log_file_name%
