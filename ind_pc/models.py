from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from assets.models import Base, Department
from it_purchase_list.models import Supplier
# 追踪日志
from auditlog.registry import auditlog


class DeviceType(models.Model):
    """
    设备类型模型
    """
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, verbose_name="供应商")
    name = models.CharField(max_length=255, unique=True, verbose_name="设备名称")
    model = models.CharField(max_length=255, verbose_name="设备型号")
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="创建人")
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间")
    note = models.TextField(blank=True, null=True, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "设备类型"
        verbose_name_plural = "设备类型"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class IndustrialPC(models.Model):
    """
    工控机信息模型
    """
    # 系统类型
    SYSTEM_VERSION_CHOICES = (
        ('win_xp', 'Windows XP'),
        ('win7_home', 'Windows 7 家庭版'),
        ('win7_emb', 'Windows 7 嵌入式(Embedded)'),
        ('win7_pro', 'Windows 7 专业版'),
        ('win7_ultimate', 'Windows 7 旗舰版'),
        ('win8_pro', 'Windows 8 专业版'),
        ('win8_1', 'Windows 8.1'),
        ('win10_home', 'Windows 10 家庭版'),
        ('win10_pro', 'Windows 10 专业版'),
        ('win10_enterprise', 'Windows 10 企业版'),
        ('win10_enterprise_LTSC', 'Windows 10 企业版 LTSC'),
        ('win10_ultimate', 'Windows 10 旗舰版'),
        ('win11_home', 'Windows 11 家庭版'),
        ('win11_pro', 'Windows 11 专业版'),
        ('win11_enterprise', 'Windows 11 企业版'),
        ('ubuntu_18_04', 'Ubuntu 18.04 LTS'),
        ('ubuntu_20_04', 'Ubuntu 20.04 LTS'),
        ('ubuntu_22_04', 'Ubuntu 22.04 LTS'),
        ('centos_7', 'CentOS 7'),
        ('centos_8', 'CentOS 8'),
        ('rhel_7', '红帽企业 Linux 7'),
        ('rhel_8', '红帽企业 Linux 8'),
    )
    # 设备运行状态
    OPERATING_STATUS_CHOICES = (
        ('normal', '正常运行'),
        ('fault', '故障状态'),
        ('repair', '维修状态'),
        ('not_used', '未启用状态'),
        ('other', '其他状态'),
    )
    # 设备数据采集方式
    COLLECTION_DATA_TYPE = (
        ('database', '数据库IP采集'),
        ('esop', 'ESOP防重软件采集'),
        ('machine_database', '项目机数据库IP采集'),
        ('xianda', '先达数控IP采集'),
        ('other', '其他方式采集'),
        ('no_collection', '未采集')
    )

    asset_number = models.CharField(
        max_length=255, blank=True, unique=True, verbose_name="固定资产编号")
    business_line = models.ForeignKey(
        Base, on_delete=models.CASCADE, verbose_name="事业线")
    workshop = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="车间")
    location = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="设备位置")
    device_supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, verbose_name="设备供应商", related_name="industrial_pcs")
    device_name = models.ForeignKey(
        DeviceType, on_delete=models.SET_NULL, null=True, verbose_name="设备名称")
    device_model = models.CharField(
        max_length=255, blank=True, verbose_name="设备型号")
    device_alias = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="设备别名")
    device_att = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="设备加工属性")
    device_number = models.CharField(
        max_length=255, blank=True, unique=True, null=True, verbose_name="设备编号")
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="IP地址")
    mac_address = models.CharField(
        max_length=17, blank=True, null=True, verbose_name="MAC地址")
    system_version = models.CharField(
        max_length=255, verbose_name="系统版本",
        blank=True, null=True, choices=SYSTEM_VERSION_CHOICES,
        default='win7_pro')
    system_type = models.CharField(max_length=50, verbose_name="系统类型", blank=True, null=True, choices=(
        ("32", "32位操作系统"), ("64", "64位操作系统")), default='64')
    admin_account = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="管理员账号")
    password = models.CharField(max_length=255, blank=True, null=True, verbose_name="密码")
    vnc_password = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="VNC密码")
    antivirus_installed = models.BooleanField(
        default=False, verbose_name="是否安装杀毒软件")
    network_connected = models.BooleanField(
        default=False, verbose_name="是否连接网络")
    operating_status = models.CharField(
        max_length=100,
        choices=OPERATING_STATUS_CHOICES,
        default='normal',
        verbose_name="设备运行状态"
    )
    hardening = models.BooleanField(default=False, verbose_name="是否加固")
    hardening_date = models.DateField(
        blank=True, null=True, verbose_name="加固日期")
    hardening_strategy = models.TextField(
        blank=True, null=True, verbose_name="加固策略")
    hardening_operator = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="加固操作人")
    backed_up = models.BooleanField(default=False, verbose_name="是否备份")
    backup_date = models.DateField(blank=True, null=True, verbose_name="备份日期")
    backup_operator = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="备份操作人")
    collection = models.BooleanField(default=False, verbose_name="是否支持采集数据")
    collection_data = models.BooleanField(
        default=False, verbose_name="是否采集数据")
    collection_type = models.CharField(
        max_length=100,
        choices=COLLECTION_DATA_TYPE,
        default='no_collection',
        blank=True,
        null=True,
        verbose_name="采集方式")
    program_path = models.BooleanField(default=False, verbose_name="程序路径是否切换")
    program_dll = models.BooleanField(default=False, verbose_name="先达设备dll文件是否配置")
    horizontal_trough = models.BooleanField(default=False, verbose_name="先达设备“忽略水平槽”是否打开")
    collection_operator = models.CharField(max_length=100, blank=True, null=True, verbose_name="采集操作人")
    collection_date = models.DateField(blank=True, null=True, verbose_name="设置采集日期")
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="创建人")
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间")
    note = models.TextField(blank=True, null=True, verbose_name="备注")

    def __str__(self):
        return self.asset_number

    def get_device_model(self):
        if self.device_name:  # 确保关联的设备名称存在
            return self.device_name.model
        return ''  # 如果没有设备名称，则返回空字符串

    class Meta:
        verbose_name = "工控机信息"
        verbose_name_plural = "工控机信息"

    def clean(self):
        if self.network_connected and (not self.ip_address):
            raise ValidationError("如果网络已连接，IP地址必须填写。")

    def save(self, *args, **kwargs):
        # 如果设备类型被设置了，同时设备供应商为空，自动设置设备供应商
        if self.device_name and not self.device_supplier:
            self.device_supplier = self.device_name.supplier

        # 基于设备供应商设置管理员账号和密码
        if self.device_supplier:
            if self.device_supplier.name == "豪迈":
                self.admin_account = self.admin_account or "hgservice"
                self.password = self.password or "Homag"
            elif self.device_supplier.name == "谢林":
                self.admin_account = self.admin_account or "Admin"
                self.password = self.password or "austria"

        # 调用父类的save方法来处理实际的保存逻辑
        super().save(*args, **kwargs)


auditlog.register(DeviceType)
auditlog.register(IndustrialPC)
