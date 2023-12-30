from django.conf import settings
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.core.checks import messages
from django.http import HttpResponseRedirect
from import_export.admin import ImportExportModelAdmin
from .models import Purchase, Supplier, NetworkDevice
from pub.resources import PurchaseResource, NetworkDeviceResource


@admin.register(Purchase)
class PurchaseAdmin(ImportExportModelAdmin):
    change_list_template = 'admin/change_list.html'
    resource_class = PurchaseResource
    list_display = ('cost_number', 'spare_part_type', 'spare_part', 'department', 'supplier',
                    'quantity', 'created_by', 'unit_price', 'total_price', 'account_status', 'account_completed_date')
    list_filter = (
        'created_by', 'spare_part_type', 'base_name__name', 'department__name', 'supplier__name', 'account_status',
        ('application_date', DateFieldListFilter), ('account_completed_date', DateFieldListFilter))
    search_fields = ('created_by', 'spare_part_type__name', 'spare_part', 'department__name',
                     'supplier__name', 'cost_number', 'unit_price', 'invoice_number',)
    readonly_fields = ['account_completed_date']
    list_per_page = 20  # 设置每页显示20条记录

    def get_readonly_fields(self, request, obj=None):
        # 获取所有字段名
        all_fields = [field.name for field in self.model._meta.fields]
        # 超级管理员可以编辑所有字段
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)

        # 供应商组可以修改'发货状态'和'发货单号'字段，其他字段为只读
        if request.user.groups.filter(name='供应商').exists():
            return [field for field in all_fields if field not in ['delivery_status', 'delivery_number']]

        # 默认情况下，所有字段都是只读的
        return all_fields

    def has_change_permission(self, request, obj=None):
        # 如果用户是超级管理员，允许修改
        if request.user.is_superuser:
            return True

        # 如果用户属于供应商组，允许修改
        if request.user.groups.filter(name='供应商').exists():
            return True

        # 默认不允许修改
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # 如果用户是超级管理员，返回所有记录
        if request.user.is_superuser:
            return qs

        # 如果用户关联了assets应用的Supplier模型
        if hasattr(request.user, 'supplier'):
            # 获取assets应用的Supplier模型中与当前用户相关联的Supplier实例的名称
            supplier_name = request.user.supplier.name
            # 过滤当前Purchase模型的记录，仅返回与supplier_name匹配的记录
            return qs.filter(supplier__name=supplier_name)

        # 如果用户不是超级管理员也没有关联的供应商，返回空查询集
        return qs.none()

    # 增加自定义按钮
    actions = ['quantity_total', 'supplier_spare_parts_type']

    def quantity_total(self, request, queryset):
        pass

    def supplier_spare_parts_type(self, request, queryset):
        pass

    quantity_total.short_description = ' 各基地部门采购数量及总价分析'
    supplier_spare_parts_type.short_description = ' 供应商备件类型总价分析'
    quantity_total.icon = 'fa-solid fa-screwdriver-wrench'
    supplier_spare_parts_type.icon = "fa-solid fa-money-check-dollar"
    quantity_total.type = 'success'
    supplier_spare_parts_type.type = 'primary'
    quantity_total.style = 'color:black;'
    supplier_spare_parts_type.style = 'color:black;'
    quantity_total.action_type = 1
    quantity_total.action_url = f'{settings.BASE_URL}/it_purchase_list/sunburst-chart/'
    supplier_spare_parts_type.action_type = 1
    supplier_spare_parts_type.action_url = f'{settings.BASE_URL}/it_purchase_list/rose-chart/'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'contact_phone', 'is_active')
    list_filter = ('name', 'contact_person', 'is_active')
    search_fields = ('name', 'contact_person',)


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(ImportExportModelAdmin):
    resource_class = NetworkDeviceResource
    list_display = ('name', 'brand', 'type', 'model', 'ip_address', 'rack_position',
                    'supplier_info', 'maintenance_status', 'web_link_display')
    search_fields = ('name', 'ip_address', 'serial_number', 'location')
    list_filter = ('brand', 'type', 'maintenance_status', 'location', ('purchase_date', DateFieldListFilter))
    readonly_fields = ('out_of_warranty_date',
                       'maintenance_status', 'web_link_display')
    list_per_page = 20  # 设置每页显示20条记录

    def import_action(self, request, *args, **kwargs):
        """
        重写导入动作处理导入时的错误。
        """
        try:
            return super().import_action(request, *args, **kwargs)
        except UnicodeDecodeError:
            self.message_user(
                request, "文件编码错误，请使用UTF-8或GBK编码的CSV文件。", level=messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('username', 'password')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.exclude(username__isnull=False, password__isnull=False)

    def has_view_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return False if (obj.username and obj.password) else True
        return super().has_view_permission(request, obj=obj)

    def supplier_info(self, obj):
        return f"{obj.supplier.name} / {obj.supplier.contact_person} / {obj.supplier.contact_phone}"

    supplier_info.short_description = "供应商信息"
