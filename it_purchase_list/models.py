import datetime
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from assets.models import SparePartType, Base, Department
# 追踪日志
from auditlog.registry import auditlog


class Supplier(models.Model):
    """
    IT类采购清单供应商模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")
    contact_person = models.CharField(
        max_length=100, verbose_name="对接人", blank=True, null=True)
    contact_phone = models.CharField(
        max_length=20, verbose_name="对接电话", blank=True, null=True)
    address = models.CharField(
        max_length=255, verbose_name="地址", blank=True, null=True)
    remarks = models.CharField(
        max_length=255, verbose_name="备注", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "采购供应商"
        verbose_name_plural = "采购供应商"


class Purchase(models.Model):
    """
    IT类采购清单登记表
    """
    # 报账状态选项
    ACCOUNT_STATUS_CHOICES = (
        ('unclaimed', '未报账'),
        ('submitted', '已提单'),
        ('claimed', '已报账'),
        ('discarded', '废弃单据'),
        ('other', '其他'),
    )
    DELIVERY_STATUS_CHOICES = (
        ('undelivered', '未发货'),
        ('delivered', '已发货'),
        ('arrived', '已到货'),
        ('returned', '已退货'),
        ('other', '其他'),
    )
    spare_part_type = models.ForeignKey(
        SparePartType, on_delete=models.CASCADE, verbose_name="设备名称")
    spare_part = models.CharField(max_length=255, verbose_name="设备型号")
    base_name = models.ForeignKey(
        Base, on_delete=models.CASCADE, verbose_name="基地名称")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="费用部门")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, verbose_name="采购供应商")
    quantity = models.IntegerField(verbose_name="数量")
    unit = models.CharField(max_length=50, verbose_name="单位")
    applicant = models.CharField(max_length=100, verbose_name="申请人")
    applicant_phone = models.CharField(max_length=20, verbose_name="申请人电话")
    application_date = models.DateField(
        default=datetime.date.today, verbose_name="申请日期")
    cost_number = models.CharField(max_length=100, verbose_name="费用单号")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="单价")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="总价", editable=False)
    created_by = models.CharField(max_length=100, verbose_name="创建人")
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='undelivered',  # 默认值为 "未发货"
        verbose_name="发货状态",
    )
    delivery_number = models.CharField(
        max_length=150, verbose_name="运单号", blank=True, null=True)
    # 报账状态字段
    account_status = models.CharField(
        max_length=20,
        choices=ACCOUNT_STATUS_CHOICES,
        default='unclaimed',  # 默认值为 "未报账"
        verbose_name="报账状态"
    )
    account_completed_date = models.DateTimeField(
        verbose_name="报账完成时间", blank=True, null=True, editable=False
    )
    invoice_number = models.CharField(
        max_length=150, verbose_name="发票号", blank=True, null=True)
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        if self.account_status in ['claimed', 'discarded'] and not self.account_completed_date:
            self.account_completed_date = now()
        super(Purchase, self).save(*args, **kwargs)
        # super().save(*args, **kwargs)

    def __str__(self):
        return f"费用单号 {self.cost_number}"

    class Meta:
        verbose_name = "IT采购列表"
        verbose_name_plural = "IT采购列表"


class NetworkDevice(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('switch', '交换机'),
        ('router', '路由器'),
        ('network_card', '网卡'),
        ('firewall', '防火墙'),
        ('woc', 'WOC'),
        ('ac', 'AC行为管理'),
        ('ap', '无线控制器'),
    ]
    MAINTENANCE_STATUS_CHOICES = [
        ('under_maintenance', '维保中'),
        ('out_of_maintenance', '已过保'),
    ]

    brand = models.CharField(max_length=100, verbose_name="设备品牌")
    type = models.CharField(
        max_length=50, choices=DEVICE_TYPE_CHOICES, default='switch', verbose_name="类型")
    name = models.CharField(max_length=100, verbose_name="设备名称")
    model = models.CharField(max_length=100, verbose_name="设备型号")
    ip_address = models.GenericIPAddressField(verbose_name="设备IP")
    purpose = models.TextField(verbose_name="用途")
    serial_number = models.CharField(max_length=100, verbose_name="设备序列号")
    web_link = models.URLField(verbose_name="链接", blank=True, null=True)
    purchase_date = models.DateField(default=now, verbose_name="购买日期")
    warranty_period = models.IntegerField(verbose_name="质保期（天）")
    out_of_warranty_date = models.DateField(
        verbose_name="过保日期", blank=True, null=True)
    location = models.CharField(max_length=100, verbose_name="所在机房")
    rack_position = models.CharField(max_length=100, verbose_name="机架位置")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, verbose_name="供应商")
    maintenance_status = models.CharField(
        max_length=50, choices=MAINTENANCE_STATUS_CHOICES, verbose_name="维保状态")
    service_object = models.CharField(
        max_length=100, verbose_name="服务对象", blank=True, null=True)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="采购价格")
    net_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="资产净值", blank=True, null=True)
    username = models.CharField(
        max_length=100, verbose_name="账号", blank=True, null=True)
    password = models.CharField(
        max_length=100, verbose_name="密码", blank=True, null=True)
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.purchase_date and self.warranty_period:
            self.out_of_warranty_date = self.purchase_date + \
                datetime.timedelta(days=self.warranty_period)
            self.maintenance_status = 'under_maintenance' if self.out_of_warranty_date > now(
            ).date() else 'out_of_maintenance'
        super().save(*args, **kwargs)

    def web_link_display(self):
        if self.web_link:
            return mark_safe(f'<a href="{self.web_link}" target="_blank">{self.web_link}</a>')
        return "N/A"
    web_link_display.short_description = "链接"

    class Meta:
        verbose_name = "网络设备"
        verbose_name_plural = "网络设备"


auditlog.register(Supplier)
auditlog.register(Purchase)
auditlog.register(NetworkDevice)
