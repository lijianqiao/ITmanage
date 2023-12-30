from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from .models import Asset, MaintenanceRecord, SparePart, Supplier, AssetManager, Department, SparePartType, Base
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from pub.resources import MaintenanceRecordResource, AssetResource, SupplierResource


def get_full_name(user):
    """
    获取用户的完整姓名
    """
    return f"{user.last_name} {user.first_name}".strip()


class CustomUserCreationForm(UserCreationForm):
    """
    自定义创建用户模板
    """
    first_name = forms.CharField(label='名称', required=True)
    last_name = forms.CharField(label='姓氏', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('last_name', 'first_name',)


class UserAdmin(BaseUserAdmin):
    """
    管理用户显示
    """
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'last_name', 'first_name', 'email'),
        }),
    )
    list_display = ('username', 'email', 'get_full_name', 'is_staff')
    list_per_page = 20  # 设置每页显示20条记录

    def get_full_name(self, obj):
        return get_full_name(obj)

    get_full_name.short_description = '姓名'  # 设置列的标题


@admin.register(Asset)
class AssetAdmin(ImportExportModelAdmin):
    """
    资产列表管理：创建、删除
    """
    resource_class = AssetResource
    related_field = 'asset_manager'
    change_form_template = 'assets/change_form.html'
    list_display = ('name', 'sn', 'department',
                    'purchase_date', 'status')  # 自定义列表显示
    # 允许通过名称和序列号搜索资产
    search_fields = ('name', 'sn', 'description', 'user',
                     'department__name', 'supplier__name', 'status')
    # 使用基地、供应商名字设置过滤器
    list_filter = ('department__base__name', 'supplier__name', ('purchase_date', DateFieldListFilter))
    list_per_page = 20  # 设置每页显示20条记录

    # 添加一个自定义的方法来生成“查看维修记录”的链接
    def repairs_list_url(self, obj):
        # 这里假设您的应用名是 'assets'，并且您已经在 admin 中注册了 MaintenanceRecord
        url = reverse('admin:assets_maintenancerecord_changelist')
        # 返回一个包含查询参数的URL，该参数将资产ID与维修记录关联起来
        return format_html('<a href="{}?asset__id__exact={}">查看维修记录</a>', url, obj.id)

    # 增加自定义表单的链接
    def get_custom_form_url(self, obj):
        # 获取当前资产的部门ID
        department_id = obj.department_id if obj.department else ''
        # 尝试获取名为'成都运维组'的供应商ID
        try:
            default_supplier = Supplier.objects.get(name='成都运维组')
            supplier_id = default_supplier.id
        except Supplier.DoesNotExist:
            supplier_id = ''  # 或者设定为您系统中的默认供应商ID
        # 生成维修登记的URL
        url = reverse('admin:assets_maintenancerecord_add')
        # 返回一个包含资产ID和部门ID参数的链接
        return format_html('<a href="{}?asset={}&department={}&supplier={}">维修登记</a>', url, obj.id, department_id, supplier_id)

    # 更改表单视图以包含自定义链接
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            asset_obj = self.get_object(request, object_id)
            # 添加维修登记的链接
            extra_context['custom_form_url'] = self.get_custom_form_url(asset_obj)
            # 添加查看维修记录的链接
            extra_context['repairs_list_url'] = self.repairs_list_url(asset_obj)
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    # 增加列名描述
    get_custom_form_url.short_description = "快速维修登记"
    repairs_list_url.short_description = "该资产维修记录"
    # 在readonly_fields中添加这个方法的名称
    readonly_fields = ['qr_code_preview',
                       'repairs_list_url', 'get_custom_form_url']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        # 超级管理员看到所有资产
        if user.is_superuser:
            return qs

        # 检查用户是否属于供应商组
        if user.groups.filter(name='供应商').exists():
            # 如果是，显示所有资产
            return qs

        # 如果用户是资产管理员，仅显示其部门的资产
        if hasattr(user, 'asset_manager'):
            # return qs.filter(department=user.asset_manager.department)
            # 使用select_related来减少数据库查询
            return qs.filter(department__asset_manager__user=user).select_related('department', 'supplier')

        # 如果用户不是超级管理员、供应商组成员或资产管理员，不显示任何资产
        return qs.none()

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="150" id="qr-code" />', obj.qr_code.url)
        return "二维码未生成"

    qr_code_preview.short_description = "二维码预览"

    def delete_model(self, request, obj):
        """在Django admin中删除对象时调用此方法。"""
        # 在这里调用模型的delete方法
        obj.delete()


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(ImportExportModelAdmin):
    """
    维修记录管理：创建、删除
    """
    resource_class = MaintenanceRecordResource
    related_field = 'supplier'
    list_display = ('asset', 'date', 'department',
                    'applicant', 'repair_status', 'repair_duration_display')
    # filter_vertical = ('spare_parts',)  # 使多对多字段易于操作
    filter_horizontal = ('spare_parts',)  # 使多对多字段易于操作
    # 允许通过资产名称、资产sn、申请维修人和维修车间搜索维修记录
    search_fields = ('asset__name', 'asset__sn',
                     'applicant', 'asset__department__name',)
    # 使用基地、供应商名字设置过滤器
    list_filter = ('department__base__name', 'supplier__name', ('date', DateFieldListFilter))
    list_per_page = 20  # 设置每页显示20条记录

    readonly_fields = ('repair_start_time_display', 'repair_duration_display',)
    exclude = ('repair_start_time', 'repair_duration',)

    def repair_start_time_display(self, obj):
        if obj.repair_start_time:
            return obj.repair_start_time.strftime('%Y-%m-%d %H:%M:%S')
        return 'N/A'
    repair_start_time_display.short_description = '维修开始时间'

    def repair_duration_display(self, obj):
        if obj.repair_duration:
            # 格式化显示维修持续时间
            duration = obj.repair_duration
            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}天{hours}小时{minutes}分钟{seconds}秒"
        return '维修中'  # 或者其他您希望显示的文本
    repair_duration_display.short_description = '维修持续时间'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # 移除在界面上不需要直接编辑的字段
        fields = [f for f in fields if f not in (
            'repair_start_time', 'repair_duration')]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        # 检查用户是否关联了供应商
        if hasattr(user, 'supplier'):
            # 只返回与该供应商相关的维修记录
            return qs.filter(supplier=user.supplier).select_related('supplier', 'department')

        # 如果用户是资产管理员，仅显示其部门的维修记录
        if hasattr(user, 'asset_manager'):
            return qs.filter(department=user.asset_manager.department).select_related('department', 'supplier')

        # 其他用户不显示任何记录
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # 确保这是创建表单的请求
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            if 'asset' in request.GET:
                try:
                    asset_id = request.GET['asset']
                    asset = Asset.objects.get(pk=asset_id)
                    kwargs['initial']['department'] = asset.department
                except (Asset.DoesNotExist, ValueError):
                    pass
        return form

    def save_model(self, request, obj, form, change):
        # 如果这是一个变更表单，并且用户不是超级用户也不是资产管理员
        if change and not request.user.is_superuser and not hasattr(request.user, 'asset_manager'):
            # 保存模型前不更改维修状态字段
            form.cleaned_data.pop('repair_status', None)

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # 如果用户属于供应商组，允许修改记录
        if request.user.groups.filter(name='供应商').exists():
            return True
        return super().has_change_permission(request, obj=obj)

    def has_view_permission(self, request, obj=None):
        # 如果用户属于供应商组，允许查看记录
        if request.user.groups.filter(name='供应商').exists():
            return True
        return super().has_view_permission(request, obj=obj)

    # 增加自定义按钮
    actions = ['custom_button']

    def custom_button(self, request, queryset):
        pass
    custom_button.short_description = ' 维修类型报表'
    custom_button.icon = 'fa-solid fa-screwdriver-wrench'
    custom_button.type = 'success'
    custom_button.style = 'color:black;'
    custom_button.action_type = 1
    custom_button.action_url = f'{settings.BASE_URL}/assets/maintenance_report_analysis/'


@admin.register(SparePartType)
class SparePartTypeAdmin(admin.ModelAdmin):
    """
    备件类型管理：创建、删除
    """
    list_display = ('name',)


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    """
    备件管理：创建、删除
    """
    list_display = ('type', 'name', 'sn', 'warranty_period', 'created_at')
    list_filter = ('type',)
    search_fields = ('type__name', 'name', 'sn',)  # 允许通过名称和序列号搜索备件

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "supplier":
            kwargs["queryset"] = Supplier.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Supplier)
class SupplierAdmin(ImportExportModelAdmin):
    """
    供应商管理：创建、删除
    """
    resource_class = SupplierResource
    list_display = ('name', 'contact_person', 'contact_phone')
    search_fields = ('name', 'contact_person',)  # 允许通过供应商名称和对接人搜索供应商


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    """
    基地管理：创建、删除
    """
    list_display = ('name',)


class AssetManagerForm(forms.ModelForm):
    """
    资产管理员管理：全称
    """
    class Meta:
        model = AssetManager
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AssetManagerForm, self).__init__(*args, **kwargs)
        self.fields[
            'user'].label_from_instance = lambda obj: f"{obj.username} - {get_full_name(obj)}"


@admin.register(AssetManager)
class AssetManagerAdmin(admin.ModelAdmin):
    """
    资产管理员管理：创建、删除
    """
    form = AssetManagerForm
    list_display = ('user', 'get_full_name', 'base', 'employee_number')
    list_filter = ('base',)
    # search_fields = ('user', 'employee_number',)
    # 允许通过名称和工号搜索资产管理员
    search_fields = ('user__username', 'user__first_name',
                     'user__last_name', 'employee_number',)

    def get_full_name(self, obj):
        # 这里假设 'user' 是与 AssetManager 相关联的 User 实例
        # 返回用户的全名，首先是姓氏，然后是名字
        return get_full_name(obj.user)

    get_full_name.short_description = '姓名'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            asset_manager = request.user.asset_manager
            return qs.filter(department=asset_manager.department)
        except AssetManager.DoesNotExist:
            return qs.none()


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    部门管理：创建、删除
    """
    list_display = ('name', 'base', 'asset_manager')
    search_fields = ('name',)  # 允许通过部门名称搜索部门
    # 使用基地、供应商名字设置过滤器
    list_filter = ('base',)


# 重新注册 User 模型以使用新的 UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.site_header = 'IT资产管理平台'  # 设置header
admin.site.site_title = 'IT资产管理平台'   # 设置title
admin.site.index_title = 'IT资产管理平台'
