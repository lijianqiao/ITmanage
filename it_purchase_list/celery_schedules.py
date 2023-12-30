# it_purchase_list/celery_schedules.py

from django_celery_beat.models import PeriodicTask, IntervalSchedule


def create_periodic_task():
    # 创建一个每2分钟运行一次的调度
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=2,
        period=IntervalSchedule.MINUTES
    )

    # 创建或更新周期性任务
    PeriodicTask.objects.update_or_create(
        name='Check Network Device Status Every 2 Minutes',
        defaults={
            'interval': schedule,
            'task': 'it_purchase_list.tasks.check_network_devices_status'
        }
    )


create_periodic_task()
