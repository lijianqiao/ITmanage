import qrcode
from io import BytesIO
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now
# 追踪日志
from auditlog.registry import auditlog


class Supplier(models.Model):
    """
    供应商模型
    """
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, related_name='supplier')
    name = models.CharField(max_length=100, verbose_name="名称")
    contact_person = models.CharField(max_length=100, verbose_name="对接人")
    contact_phone = models.CharField(max_length=20, verbose_name="对接电话")
    address = models.TextField(verbose_name="地址")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "供应商"
        verbose_name_plural = "供应商"


class Base(models.Model):
    """
    基地模型
    """
    name = models.CharField(max_length=100, verbose_name="基地名称")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "基地"
        verbose_name_plural = "基地"


class Department(models.Model):
    """
    部门模型
    """
    name = models.CharField(max_length=100, verbose_name="部门名称")
    base = models.ForeignKey(Base, on_delete=models.CASCADE, verbose_name="基地")
    asset_manager = models.ForeignKey(
        'AssetManager',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="资产管理员",
        related_name="managed_departments"
    )

    def __str__(self):
        return f"{self.base.name} - {self.name}"

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"


class AssetManager(models.Model):
    """
    资产管理员模型
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='asset_manager')
    base = models.ForeignKey(
        Base, on_delete=models.SET_NULL, null=True, verbose_name="基地")
    employee_number = models.CharField(max_length=50, verbose_name="工号")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="部门")

    def __str__(self):
        return f"{self.user.last_name}{self.user.first_name} - {self.base.name}"

    class Meta:
        verbose_name = "资产管理员"
        verbose_name_plural = "资产管理员"


def department_path(instance, filename):
    """
    二维码上传路径
    """
    # 文件将上传到MEDIA_ROOT/qr_codes/<department_id>/<filename>
    return '{0}/{1}/{2}'.format(instance.department.base.name, instance.department.name, filename)


class Asset(models.Model):
    """
    资产模型
    """
    ASSETS_STATUS = (
        ('normal', '正常'),
        ('scrap', '报废'),
        ('repair', '维修'),
        ('depreciation', '折旧'),
        ('other', '其他'),
    )
    name = models.CharField(max_length=100, verbose_name="名称")
    sn = models.CharField(max_length=100, unique=True, verbose_name="序列号")
    description = models.TextField(verbose_name="描述")
    purchase_date = models.DateField(verbose_name="采购日期")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, verbose_name="供应商")
    warranty_period = models.IntegerField(verbose_name="质保期")
    user = models.CharField(max_length=100, verbose_name="领用人")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="使用部门")
    status = models.CharField(
        max_length=100,
        choices=ASSETS_STATUS,
        default='normal',
        verbose_name="资产状态")
    qr_code = models.ImageField(
        upload_to=department_path,
        blank=True,
        null=True,
        verbose_name="二维码"
    )
    repair_count = models.IntegerField(default=0, verbose_name="维修次数")

    def __str__(self):
        return f"{self.name} ({self.sn})"

    class Meta:
        verbose_name = "资产"
        verbose_name_plural = "资产"

    def save(self, *args, **kwargs):
        # 先调用save方法以填充self.pk（如果是新对象）
        super().save(*args, **kwargs)
        # 仅当不存在二维码时生成并保存二维码
        if not self.qr_code:
            self.generate_qr_code()
            # 用新的二维码再次保存对象
            super().save(*args, **kwargs)

    def generate_qr_code(self):
        # 生成二维码的逻辑在这里
        qr_content = f"{settings.PUBLIC_URL}/admin/assets/asset/{self.pk}/change/"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_codes/{self.name}_{self.sn}_{self.pk}.png'
        self.qr_code.save(filename, File(buffer), save=False)

    def delete(self, *args, **kwargs):
        # 如果文件存在则删除
        if self.qr_code:
            self.qr_code.delete(save=False)
        super().delete(*args, **kwargs)


@receiver(post_delete, sender=Asset)
def delete_qr_code(sender, instance, **kwargs):
    """
    连接 post_delete 信号到 Asset 模型的接收器，删除二维码触发
    """
    if instance.qr_code:
        instance.qr_code.delete(save=False)


class SparePartType(models.Model):
    """
    备件类型模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="备件类型名称")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "备件类型"
        verbose_name_plural = "备件类型"


class SparePart(models.Model):
    """
    备件模型
    """
    type = models.ForeignKey(
        SparePartType, on_delete=models.CASCADE, verbose_name="备件类型")
    name = models.CharField(max_length=100, verbose_name="型号名称")
    sn = models.CharField(max_length=100, unique=True, verbose_name="序列号")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供应商")
    warranty_period = models.IntegerField(verbose_name="配件质保期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return f"{self.type.name} - {self.name} ({self.sn})"

    class Meta:
        verbose_name = "备件"
        verbose_name_plural = "备件"


class MaintenanceRecord(models.Model):
    """
    维修记录模型
    """
    REPAIR_STATUS_CHOICES = (
        ('repairing', '维修中'),
        ('arrived', '已送至供应商'),
        ('repaired', '已维修'),
        ('norepaire', '不维修'),
        ('discarded', '已废弃'),
    )
    MAINTENANCE_TYPE_CHOICES = (
        ('return', '返回供应商维修'),
        ('general', '信息部维修'),
        ('warranty', '供应商保修'),
        ('other', '其他维修'),
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, verbose_name="对应资产")
    date = models.DateField(default=now, verbose_name="维修日期")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="维修部门")
    applicant = models.CharField(max_length=100, verbose_name="申请维修人")
    description = models.TextField(verbose_name="维修描述")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, verbose_name="维修供应商")
    maintenance_type = models.CharField(
        max_length=100,
        choices=MAINTENANCE_TYPE_CHOICES,
        default='return',
        verbose_name="维修类别")
    spare_parts = models.ManyToManyField(
        SparePart, verbose_name="维修配件", blank=True)
    repair_status = models.CharField(
        max_length=100,
        choices=REPAIR_STATUS_CHOICES,
        default='repairing',
        verbose_name='维修状态'
    )
    repair_start_time = models.DateTimeField(
        verbose_name="维修开始时间", blank=True, null=True)
    repair_duration = models.DurationField(
        verbose_name="维修持续时间", blank=True, null=True)

    def __str__(self):
        return f"{self.asset.name} - {self.date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        # 首次创建对象时，增加相关联资产的维修次数
        if not self.pk:
            self.asset.repair_count += 1
            self.asset.save()
        # 当状态变为'已送至供应商'时，设置开始时间
        if self.repair_status == 'arrived' and not self.repair_start_time:
            self.repair_start_time = now()
        # 当维修状态改变为'已维修'或'已废弃'时，计算持续时间
        elif self.repair_status in ['repaired', 'discarded', 'norepaire'] and self.repair_start_time:
            self.repair_duration = now() - self.repair_start_time
            self.repair_start_time = None  # 可选：清空开始时间
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "维修记录"
        verbose_name_plural = "维修记录"


auditlog.register(Supplier)
auditlog.register(Base)
auditlog.register(Department)
auditlog.register(AssetManager)
auditlog.register(Asset)
auditlog.register(SparePartType)
auditlog.register(SparePart)
auditlog.register(MaintenanceRecord)
