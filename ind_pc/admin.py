from django.conf import settings
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter, SimpleListFilter
from .models import IndustrialPC, DeviceType
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from pub.resources import DeviceTypeResource, IndustrialPCResource


@admin.register(DeviceType)
class DeviceTypeAdmin(ImportExportModelAdmin):
    resource_class = DeviceTypeResource
    list_display = ('name', 'model', 'supplier', 'creator', 'create_time', 'note')
    search_fields = ('name', 'model', 'supplier__name')
    list_filter = ('supplier', ('create_time', DateFieldListFilter))
    date_hierarchy = 'create_time'
    readonly_fields = ('creator', 'create_time')
    list_per_page = 20  # 设置每页显示20条记录

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super(DeviceTypeAdmin, self).save_model(request, obj, form, change)


class DeviceModelFilter(SimpleListFilter):
    """
    自定义过滤器，用于过滤设备名称下的设备型号
    """
    title = '设备型号'
    parameter_name = 'device_model'

    def lookups(self, request, model_admin):
        # 获取当前已选择的设备名称
        device_name_id = request.GET.get('device_name__id__exact')
        if device_name_id:
            # 如果已选择设备名称，只显示该设备名称下的设备型号
            device_types = DeviceType.objects.filter(id=device_name_id)
        else:
            # 如果没有选择设备名称，显示所有设备型号
            device_types = DeviceType.objects.all()
        device_models = set(device_types.values_list('model', flat=True))
        return [(model, model) for model in device_models]

    def queryset(self, request, queryset):
        if self.value():
            # 根据选择的设备型号筛选
            return queryset.filter(device_name__model=self.value())
        return queryset


@admin.register(IndustrialPC)
class IndustrialPCAdmin(ImportExportModelAdmin):
    resource_class = IndustrialPCResource
    list_display = ('get_asset_number_display', 'workshop', 'location', 'device_name', 'get_device_model',
                    'ip_address', 'network_connected', 'hardening', 'backed_up', 'collection', 'collection_data',
                    'operating_status', 'get_creator_full_name')
    search_fields = ('asset_number', 'device_number', 'device_model', 'ip_address',
                     'mac_address', 'workshop__name', 'business_line__name')
    list_filter = ('business_line', 'workshop', 'device_name', DeviceModelFilter,
                   'hardening', 'network_connected', 'backed_up', 'collection_data', 
                   'operating_status', ('create_time', DateFieldListFilter))
    date_hierarchy = 'create_time'
    readonly_fields = ('creator', 'create_time', 'view_device_name')
    fieldsets = (
        ("基本信息", {'fields': ('asset_number', 'business_line', 'workshop', 'location',
         'device_supplier', 'device_name', 'device_model', 'device_alias', 'device_number', 'device_att')}),
        ("系统信息", {
         'fields': ('system_version', 'system_type', 'admin_account', 'password', 'vnc_password', 'ip_address',
                    'mac_address', 'network_connected', 'antivirus_installed')}),
        ("加固信息", {'fields': (
            'hardening', 'hardening_date', 'hardening_strategy', 'hardening_operator')}),
        ("备份信息", {'fields': ('backed_up', 'backup_date', 'backup_operator')}),
        ("数据采集信息", {'fields': (
            'collection', 'collection_data', 'collection_type', "program_path", "program_dll",
            "horizontal_trough", "collection_operator", "collection_date")}),
        ("附加信息", {'fields': ('operating_status', 'note')}),
    )
    list_per_page = 20  # 设置每页显示20条记录

    def get_creator_full_name(self, obj):
        """
        在列表显示中获取用户的全名。
        """
        if obj.creator:
            return f"{obj.creator.last_name}{obj.creator.first_name}"
        return ""

    get_creator_full_name.short_description = '创建人'

    def get_asset_number_display(self, obj):
        """
        自定义显示固定资产编号的方法，如果为空则显示默认文本
        """
        return obj.asset_number if obj.asset_number else "暂无固定资产"

    get_asset_number_display.short_description = '固定资产编号'

    def get_device_model(self, obj):
        return obj.get_device_model()

    get_device_model.short_description = '设备型号'
    # 如果需要让这个字段在admin中可排序，需要设置这个
    get_device_model.admin_order_field = 'device_name__model'

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super(IndustrialPCAdmin, self).save_model(request, obj, form, change)

    # 显示相关设备类型链接的自定义方法
    def view_device_name(self, obj):
        if obj.device_name:
            url = reverse("admin:ind_pc_devicetype_change",
                          args=(obj.device_name.pk,))
            return format_html('<a href="{}">{}</a>', url, obj.device_name)
        return "-"
    view_device_name.short_description = "查看设备类型"

    # 增加自定义按钮
    actions = ['collection']

    def collection(self, request, queryset):
        pass

    collection.short_description = ' 工控机加固比例'
    collection.icon = 'fa-solid fa-shield'
    collection.type = 'success'
    collection.style = 'color:black;'
    collection.action_type = 1
    collection.action_url = f'{settings.BASE_URL}/ind_pc/industrial_pc_stats/'
