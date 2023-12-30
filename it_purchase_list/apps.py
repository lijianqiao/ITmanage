from django.apps import AppConfig
from django.db.utils import OperationalError


class ItPurchaseListConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "it_purchase_list"
    verbose_name = "IT资产采购清单"

    def ready(self):
        try:
            from . import celery_schedules
        except OperationalError:
            pass
