import os
from pathlib import Path
from .simpleui_config import (SIMPLEUI_ANALYSIS, SIMPLEUI_CONFIG, SIMPLEUI_DEFAULT_THEME,
                              SIMPLEUI_HOME_INFO, SIMPLEUI_STATIC_OFFLINE)
from .redis_config import *


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = os.getenv('BASE_URL', 'http://www.itmanage.lijianqiao.cn:8050')
PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://www.itmanage.lijianqiao.cn:8050')
FLOWER_URL = os.getenv('FLOWER_URL', 'http://www.itmanage.lijianqiao.cn:5555')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+4(ya45j$=k0ssf(agc_hs**#nnjq--)of)-55r5e3svh%a02+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['182.149.104.203', '10.11.19.14', 'www.itmanage.lijianqiao.cn', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    "simpleui",  # 修改默认后台模板为simpleui
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',                      # 解决跨域问题
    'django_celery_results',                       # 显示任务结果
    'django_celery_beat',                          # 设置定时或周期性任务
    "import_export",  # 文件导出
    "assets",  # IT资产维修应用
    "it_purchase_list",  # IT资产申购应用
    "ind_pc",   # 工控机信息应用
    # 'it_purchase_list.apps.ItPurchaseListConfig',
    'auditlog',     # 日志记录
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    'corsheaders.middleware.CorsMiddleware',    # 解决跨域问题
]

ROOT_URLCONF = "ITmanage.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 解决跨域问题
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ITmanage',
        'USER': 'root',
        'PASSWORD': 'Li123456@',
        'HOST': '127.0.0.1',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# 降低创建账户时候密码要求，现在要求至少3位，可以全部数字
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 3,
        }
    },
]

#  django的admin后台名称
ADMIN_SITE_HEADER = "IT资产管理平台"

WSGI_APPLICATION = "ITmanage.wsgi.application"

# 解决django4.0 跨域报 Cross-Origin Opener Policy错误
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'None'
CSRF_TRUSTED_ORIGINS = ['http://*.lijianqiao.cn:8050','http://182.149.104.203:8050','http://10.11.19.14:8050','http://10.11.19.14:8051']

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"
USE_TZ = False

# 设置会话过期时间为1小时
SESSION_EXPIRE_SECONDS = 60 * 60  # 1小时
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = f'{BASE_URL}/admin/login/?next=/admin/'


# 配置媒体文件路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
