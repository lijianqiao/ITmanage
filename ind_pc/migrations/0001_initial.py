# Generated by Django 4.2.7 on 2023-12-17 23:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assets', '0002_alter_maintenancerecord_spare_parts'),
        ('it_purchase_list', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='设备名称')),
                ('model', models.CharField(max_length=255, verbose_name='设备型号')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('note', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='it_purchase_list.supplier', verbose_name='供应商')),
            ],
            options={
                'verbose_name': '设备类型',
                'verbose_name_plural': '设备类型',
            },
        ),
        migrations.CreateModel(
            name='IndustrialPC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_number', models.CharField(blank=True, max_length=255, unique=True, verbose_name='固定资产编号')),
                ('location', models.CharField(blank=True, max_length=255, null=True, verbose_name='设备位置')),
                ('device_model', models.CharField(blank=True, max_length=255, verbose_name='设备型号')),
                ('device_alias', models.CharField(blank=True, max_length=255, null=True, verbose_name='设备别名')),
                ('device_att', models.CharField(blank=True, max_length=255, null=True, verbose_name='设备加工属性')),
                ('device_number', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='设备编号')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('mac_address', models.CharField(blank=True, max_length=17, null=True, verbose_name='MAC地址')),
                ('system_version', models.CharField(blank=True, choices=[('win_xp', 'Windows XP'), ('win7_home', 'Windows 7 家庭版'), ('win7_emb', 'Windows 7 嵌入式(Embedded)'), ('win7_pro', 'Windows 7 专业版'), ('win7_ultimate', 'Windows 7 旗舰版'), ('win8_pro', 'Windows 8 专业版'), ('win8_1', 'Windows 8.1'), ('win10_home', 'Windows 10 家庭版'), ('win10_pro', 'Windows 10 专业版'), ('win10_enterprise', 'Windows 10 企业版'), ('win10_enterprise_LTSC', 'Windows 10 企业版 LTSC'), ('win10_ultimate', 'Windows 10 旗舰版'), ('win11_home', 'Windows 11 家庭版'), ('win11_pro', 'Windows 11 专业版'), ('win11_enterprise', 'Windows 11 企业版'), ('ubuntu_18_04', 'Ubuntu 18.04 LTS'), ('ubuntu_20_04', 'Ubuntu 20.04 LTS'), ('ubuntu_22_04', 'Ubuntu 22.04 LTS'), ('centos_7', 'CentOS 7'), ('centos_8', 'CentOS 8'), ('rhel_7', '红帽企业 Linux 7'), ('rhel_8', '红帽企业 Linux 8')], default='win7_pro', max_length=255, null=True, verbose_name='系统版本')),
                ('system_type', models.CharField(blank=True, choices=[('32', '32位操作系统'), ('64', '64位操作系统')], default='64', max_length=50, null=True, verbose_name='系统类型')),
                ('admin_account', models.CharField(blank=True, max_length=255, null=True, verbose_name='管理员账号')),
                ('password', models.CharField(blank=True, max_length=255, null=True, verbose_name='密码')),
                ('vnc_password', models.CharField(blank=True, max_length=255, null=True, verbose_name='VNC密码')),
                ('antivirus_installed', models.BooleanField(default=False, verbose_name='是否安装杀毒软件')),
                ('network_connected', models.BooleanField(default=False, verbose_name='是否连接网络')),
                ('operating_status', models.CharField(choices=[('normal', '正常运行'), ('fault', '故障状态'), ('repair', '维修状态'), ('not_used', '未启用状态'), ('other', '其他状态')], default='normal', max_length=100, verbose_name='设备运行状态')),
                ('hardening', models.BooleanField(default=False, verbose_name='是否加固')),
                ('hardening_date', models.DateField(blank=True, null=True, verbose_name='加固日期')),
                ('hardening_strategy', models.TextField(blank=True, null=True, verbose_name='加固策略')),
                ('hardening_operator', models.CharField(blank=True, max_length=255, null=True, verbose_name='加固操作人')),
                ('backed_up', models.BooleanField(default=False, verbose_name='是否备份')),
                ('backup_date', models.DateField(blank=True, null=True, verbose_name='备份日期')),
                ('backup_operator', models.CharField(blank=True, max_length=255, null=True, verbose_name='备份操作人')),
                ('collection', models.BooleanField(default=False, verbose_name='是否支持采集数据')),
                ('collection_data', models.BooleanField(default=False, verbose_name='是否采集数据')),
                ('collection_type', models.CharField(blank=True, choices=[('database', '数据库IP采集'), ('esop', 'ESOP防重软件采集'), ('machine_database', '项目机数据库IP采集'), ('xianda', '先达数控IP采集'), ('other', '其他方式采集'), ('no_collection', '未采集')], default='no_collection', max_length=100, null=True, verbose_name='采集方式')),
                ('program_path', models.BooleanField(default=False, verbose_name='程序路径是否切换')),
                ('program_dll', models.BooleanField(default=False, verbose_name='先达设备dll文件是否配置')),
                ('horizontal_trough', models.BooleanField(default=False, verbose_name='先达设备“忽略水平槽”是否打开')),
                ('collection_operator', models.CharField(blank=True, max_length=100, null=True, verbose_name='采集操作人')),
                ('collection_date', models.DateField(blank=True, null=True, verbose_name='设置采集日期')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('note', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('business_line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.base', verbose_name='事业线')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('device_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ind_pc.devicetype', verbose_name='设备名称')),
                ('device_supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='industrial_pcs', to='it_purchase_list.supplier', verbose_name='设备供应商')),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.department', verbose_name='车间')),
            ],
            options={
                'verbose_name': '工控机信息',
                'verbose_name_plural': '工控机信息',
            },
        ),
    ]
