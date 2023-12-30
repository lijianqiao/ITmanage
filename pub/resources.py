"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: resources.py
 @DateTime: 2023/12/14 15:48
 @Docs: 各应用Django-import_export导入导出
"""

from import_export import resources, fields
from import_export.fields import Field
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, DateWidget
from django.contrib.auth.models import User
from it_purchase_list.models import Purchase, SparePartType, Base, Department, NetworkDevice
from it_purchase_list.models import Supplier as itSupplier
from assets.models import MaintenanceRecord, SparePart, Asset, Department, Supplier
from ind_pc.models import IndustrialPC, DeviceType


class DeviceTypeResource(resources.ModelResource):
    """
    ind_pc应用下设备类型的导入导出
    """
    class Meta:
        model = DeviceType


class IndustrialPCResource(resources.ModelResource):
    """
    ind_pc应用下工控机信息的导入导出
    """
    asset_number = Field(attribute='asset_number', column_name='固定资产编号')
    business_line = Field(attribute='business_line',
                          column_name='事业线', widget=ForeignKeyWidget(Base, 'name'))
    workshop = Field(attribute='workshop', column_name='车间',
                     widget=ForeignKeyWidget(Department, 'name'))
    location = Field(attribute='location', column_name='设备位置')
    device_supplier = Field(attribute='device_supplier',
                            column_name='设备供应商', widget=ForeignKeyWidget(itSupplier, 'name'))
    device_name = Field(attribute='device_name', column_name='设备名称',
                        widget=ForeignKeyWidget(DeviceType, 'name'))
    device_model = Field(attribute='device_model', column_name='设备型号')
    device_alias = Field(attribute='device_alias', column_name='设备别名')
    device_att = Field(attribute='device_att', column_name='设备加工属性')
    device_number = Field(attribute='device_number', column_name='设备编号')
    ip_address = Field(attribute='ip_address', column_name='IP地址')
    mac_address = Field(attribute='mac_address', column_name='MAC地址')
    system_version = Field(attribute='system_version', column_name='系统版本')
    system_type = Field(attribute='system_type', column_name='系统类型')
    admin_account = Field(attribute='admin_account', column_name='管理员账号')
    password = Field(attribute='password', column_name='密码')
    vnc_password = Field(attribute='vnc_password', column_name='VNC密码')
    antivirus_installed = Field(
        attribute='antivirus_installed', column_name='是否安装杀毒软件')
    network_connected = Field(
        attribute='network_connected', column_name='是否连接网络')
    operating_status = Field(
        attribute='operating_status', column_name='设备运行状态')
    hardening = Field(attribute='hardening', column_name='是否加固')
    hardening_date = Field(attribute='hardening_date',
                           column_name='加固日期', widget=DateWidget())
    hardening_strategy = Field(
        attribute='hardening_strategy', column_name='加固策略')
    backed_up = Field(attribute='backed_up', column_name='是否备份')
    backup_date = Field(attribute='backup_date',
                        column_name='备份日期', widget=DateWidget())
    hardening_operator = Field(
        attribute='hardening_operator', column_name='加固操作人')
    backup_operator = Field(attribute='backup_operator', column_name='备份操作人')
    collection = Field(attribute='collection', column_name='是否支持采集数据')
    collection_data = Field(attribute='collection_data', column_name='是否采集数据')
    collection_type = Field(attribute='collection_type', column_name='采集方式')
    program_path = Field(attribute='program_path', column_name='程序路径是否切换')
    program_dll = Field(attribute='program_dll', column_name='先达设备dll文件是否配置')
    horizontal_trough = Field(attribute='horizontal_trough', column_name='先达设备“忽略水平槽”是否打开')
    collection_operator = Field(attribute='collection_operator', column_name='采集操作人')
    collection_date = Field(attribute='collection_date', column_name='设置采集日期', widget=DateWidget())
    creator = Field(attribute='creator', column_name='创建人',
                    widget=ForeignKeyWidget(User, 'username'))
    # create_time = Field(attribute='create_time',
    #                     column_name='创建时间', widget=DateWidget())
    note = Field(attribute='note', column_name='备注')

    def dehydrate_creator(self, industrial_pc):
        """
        在导出时获取用户的全名。
        """
        if industrial_pc.creator:
            return f"{industrial_pc.creator.last_name}{industrial_pc.creator.first_name}"
        return ""

    def before_import_row(self, row, **kwargs):
        """
        Row是一个字典，代表一个即将被导入的数据行。
        """
        supplier_name = row.get('设备供应商')
        if supplier_name:
            supplier, _ = itSupplier.objects.get_or_create(
                name=supplier_name)
        else:
            # 如果没有提供供应商名称，可以设置一个默认的供应商或者抛出错误
            # 例如：supplier = itSupplier.objects.get(name='默认供应商')
            supplier = itSupplier.objects.get(name='豪迈')
            # raise ValueError("供应商名称必须提供")

        device_name = row.get('设备名称')
        device_model_str = row.get('设备型号')
        if device_name and device_model_str:
            # 这里查找或创建设备类型时，只根据名称查找，不根据型号，以防止创建重复的设备名称
            device_type, _ = DeviceType.objects.get_or_create(
                name=device_name,
                defaults={'supplier': supplier}
            )
            # 如果型号字段存在且与设备类型实例的型号不同，则更新型号
            if device_model_str and device_type.model != device_model_str:
                device_type.model = device_model_str
                device_type.save()
            # 更新row数据，以便后续导入过程可以正确处理
            print(supplier.name)
            print(supplier_name)
            row['设备名称'] = device_type.name
            row['设备型号'] = device_model_str
            row['设备供应商'] = supplier.name  # 确保供应商名称被设置

            # 检查固定资产编号字段是否为空
            if not row.get('固定资产编号'):
                # 如果为空，则设置一个默认值，例如 '暂无固定资产'
                row['固定资产编号'] = '暂无固定资产'

    class Meta:
        model = IndustrialPC
        # 从导入/导出中排除 id 字段
        exclude = ('id', 'create_time')
        import_id_fields = ('asset_number',)


class AssetResource(resources.ModelResource):
    """
    Assets应用下资产assets的导入导出
    """
    department = fields.Field(
        column_name='department_name',
        attribute='department',
        widget=ForeignKeyWidget(Department, 'name'))

    class Meta:
        model = Asset
        import_id_fields = ('sn',)
        # 这里列出您想导出的字段
        fields = ('name', 'sn', 'description', 'purchase_date', 'supplier__name', 'warranty_period', 'user',
                  'department__name', 'status', 'repair_count')


class MaintenanceRecordResource(resources.ModelResource):
    """
    Assets应用下维修记录的导入导出
    """
    # 定义一个自定义字段来显示资产的名称和序列号
    asset_detail = fields.Field(
        column_name='对应资产',
        attribute='asset',
        widget=ForeignKeyWidget(Asset, 'sn'))  # 使用 'sn' 字段来匹配相关联的资产
    # 添加一个自定义字段来表示维修配件
    spare_parts_list = fields.Field(
        column_name='维修配件',
        attribute='spare_parts',
        widget=ManyToManyWidget(SparePart, field='name'))  # 假设您想通过 'name' 字段显示备件

    def dehydrate_asset_detail(self, maintenance_record):
        """
        自定义导出资产详情的显示方式。
        """
        # 返回资产的名称和序列号的组合
        return f"{maintenance_record.asset.name} ({maintenance_record.asset.sn})"

    def dehydrate_spare_parts_list(self, maintenance_record):
        """
        自定义导出维修配件的显示方式。
        """
        # 获取所有相关联的备件的详细信息，并用逗号分隔
        parts_details = []
        for part in maintenance_record.spare_parts.all():
            # 假设你希望显示备件类型、名称和序列号
            part_detail = f"{part.type.name} - {part.name} ({part.sn})"
            parts_details.append(part_detail)

        return ', '.join(parts_details)

    class Meta:
        model = MaintenanceRecord
        # 包含自定义的字段 'asset_detail'
        fields = ('asset_detail', 'date', 'department__name', 'applicant', 'description', 'supplier__name',
                  'maintenance_type', 'spare_parts_list', 'repair_status')
        # 除了导出的字段，也可以指定导出字段的顺序
        export_order = ('asset_detail', 'date', 'department__name', 'applicant', 'description',
                        'supplier__name', 'maintenance_type', 'spare_parts_list', 'repair_status')


class SupplierResource(resources.ModelResource):
    """
    Assets应用下供应商的导入导出
    """
    class Meta:
        model = Supplier
        fields = ('name', 'contact_person', 'contact_phone', 'address')


class PurchaseResource(resources.ModelResource):
    """
    it_purchase_list应用下采购清单的导入导出
    """

    def before_import_row(self, row, **kwargs):
        # 检查并创建备件类型
        spare_part_type_name = row.get('spare_part_type')
        if spare_part_type_name:
            spare_part_type, created = SparePartType.objects.get_or_create(
                name=spare_part_type_name)
            row['spare_part_type'] = spare_part_type.id

        # 检查并创建基地
        base_name = row.get('base_name')
        if base_name:
            base, created = Base.objects.get_or_create(name=base_name)
            row['base_name'] = base.id

        # 检查并创建部门
        department_name = row.get('department')
        base_id = row.get('base_name')
        if department_name and base_id:
            department, created = Department.objects.get_or_create(
                name=department_name, base_id=base_id)
            row['department'] = department.id

        # 检查并创建供应商
        supplier_name = row.get('supplier')
        if supplier_name:
            supplier, created = itSupplier.objects.get_or_create(
                name=supplier_name)
            row['supplier'] = supplier.id

    class Meta:
        model = Purchase
        skip_unchanged = True
        report_skipped = True
        # 定义导入导出的字段
        fields = ('base_name', 'spare_part_type', 'quantity', 'unit',
                  'spare_part', 'department', 'applicant', 'applicant_phone', 'application_date',
                  'cost_number', 'unit_price', 'total_price', 'supplier', 'remarks', 'account_status', 'created_by')

    def get_instance(self, instance_loader, row):
        """
        返回None来确保总是创建新的记录，而不是基于id查找和更新现有的记录。
        """
        return None


class NetworkDeviceResource(resources.ModelResource):
    """
    it_purchase_list应用下网络设备的导入导出
    """
    purchase_date = fields.Field(
        column_name='purchase_date',
        attribute='purchase_date',
        widget=DateWidget(format='%Y/%m/%d')
    )

    def before_import_row(self, row, **kwargs):
        # 检查并创建供应商
        supplier_name = row.get('supplier')
        if supplier_name:
            supplier, created = itSupplier.objects.get_or_create(
                name=supplier_name)
            row['supplier'] = supplier.id

    class Meta:
        model = NetworkDevice
        import_id_fields = ['serial_number']  # 用其他唯一标识字段替代'id'
        # 你可以指定要导入和导出的字段
        fields = ('brand', 'type', 'name', 'model', 'ip_address', 'serial_number',
                  'web_link', 'purchase_date', 'warranty_period', 'location', 'purpose',
                  'rack_position', 'supplier', 'service_object', 'purchase_price',
                  'net_value', 'username', 'password', 'remarks')

        # exclude属性定义了哪些字段要被排除。
        exclude = ('id', )  # 通常你不会导入导出模型的自动生成ID。

    def import_data(self, dataset, *args, **kwargs):
        # 尝试UTF-8编码读取
        try:
            dataset.charset = 'utf-8'
            return super().import_data(dataset, *args, **kwargs)
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试GBK编码
            dataset.charset = 'GBK'
            return super().import_data(dataset, *args, **kwargs)
