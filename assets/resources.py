"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: resources.py
 @DateTime: 2023/11/30 9:15
 @Docs: 用于assets文件导入导出
"""
from import_export import fields, resources
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from assets.models import MaintenanceRecord, SparePart, Asset, Department, Supplier


class AssetResource(resources.ModelResource):
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
    class Meta:
        model = Supplier
        fields = ('name', 'contact_person', 'contact_phone', 'address')
