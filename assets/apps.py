from django.apps import AppConfig
from django.conf import settings


class AssetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assets"
    verbose_name = "IT资产及维修"

    def ready(self):
        from django.contrib.admin import site
        site.site_header = settings.ADMIN_SITE_HEADER

