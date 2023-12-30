"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: redis_config.py
 @DateTime: 2023/12/6 11:47
 @Docs:  redis配置
"""

# 设置缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:root@127.0.0.1:6379/3',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Broker配置，使用Redis作为消息中间件
CELERY_BROKER_URL = 'redis://:root@127.0.0.1:6379/4'

CELERY_IMPORTS = ('it_purchase_list.tasks', )

# BACKEND配置，这里使用redis
# CELERY_RESULT_BACKEND = 'redis://:root@127.0.0.1:6379/5'
CELERY_RESULT_BACKEND = 'django-db'

# 结果序列化方案
# celery内容等消息的格式设置，默认json

CELERY_IGNORE_RESULT = True
# 为任务设置超时时间，单位秒。超时即中止，执行下个任务。

# celery 的启动工作数量设置
CELERY_WORKER_CONCURRENCY = 10
CELERY_TASK_TIME_LIMIT = 5
CELERYD_FORCE_EXECV = True  # 防止死锁,应确保为True
CELERYD_PREFETCH_MULTIPLIER = 5  # 禁用任务预取
CELERYD_MAX_TASKS_PER_CHILD = 200  # worker执行50个任务自动销毁，防止内存泄露
# 单个任务的运行时间不超过此值(秒)，否则会抛出(SoftTimeLimitExceeded)异常停止任务。
CELERYD_TASK_SOFT_TIME_LIMIT = 6000
# 禁用所有速度限制，如果网络资源有限，不建议开足马力。
CELERY_DISABLE_RATE_LIMITS = True

# 任务结果过期时间，秒
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24

# celery beat配置（周期性任务设置）
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Shanghai'
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
