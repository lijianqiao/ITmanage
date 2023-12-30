import ipaddress
import json
import os

from django.core.cache import cache

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from pyecharts.options import ToolboxOpts
from assets.models import Base, Department, MaintenanceRecord, Asset
from datetime import datetime

from it_purchase_list.wechatbot import WechatWorkBot, determine_notification_details
from .models import Purchase, Supplier, NetworkDevice
from pyecharts.charts import Sunburst, Timeline
from pyecharts import options as opts
import pandas as pd
from django.shortcuts import render


def generate_sunburst_data(specific_month=None):
    """
    根据每个月的各部门购买备件类型的数量和总价绘制旭日图报表
    """
    data = []
    # 获取所有基地
    bases = Base.objects.all()
    for base in bases:
        base_total_price = 0  # 基地总价
        departments_data = []

        # 获取每个基地下的部门
        departments = Department.objects.filter(base=base)
        for department in departments:
            department_total_price = 0  # 部门总价
            spare_parts_data = []

            # 根据提供的特定日期过滤采购记录
            if specific_month:
                purchases = Purchase.objects.filter(department=department, application_date__month=specific_month.month,
                                                    application_date__year=specific_month.year)
            else:
                purchases = Purchase.objects.filter(department=department)

            spare_parts_count = {}
            for purchase in purchases:
                spare_type_name = purchase.spare_part_type.name
                count = spare_parts_count.get(
                    spare_type_name, {'count': 0, 'total_price': 0})
                count['count'] += purchase.quantity
                count['total_price'] += float(purchase.total_price)
                spare_parts_count[spare_type_name] = count

                # 累加到部门总价
                department_total_price += float(purchase.total_price)

            for spare_type, info in spare_parts_count.items():
                spare_parts_data.append({
                    "name": f"{spare_type} (数量: {info['count']}, 总价: {info['total_price']}元)",
                    "value": info['count']
                })

            departments_data.append({
                "name": f"{department.name} - 总价: {department_total_price}元",
                "children": spare_parts_data
            })

            # 累加到基地总价
            base_total_price += department_total_price

        data.append({
            "name": f"{base.name} - 总价: {base_total_price}元",
            "children": departments_data
        })

    return data


def sunburst_chart(request):
    """
    绘制旭日图, 加入时间轴
    """
    # 创建时间轴实例
    timeline = Timeline(init_opts=opts.InitOpts(
        width="1000px", height="600px"))

    # 获取所有独特的申请日期按月
    unique_months = Purchase.objects.annotate(
        month=TruncMonth('application_date')).values('month').distinct()

    # 首先创建一个不带特定日期的旭日图，它将显示所有数据
    all_data_chart = (
        Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
        .add("", generate_sunburst_data(), radius=[0, "90%"])
        .set_global_opts(title_opts=opts.TitleOpts(title="基地部门备件类型总分析 - 总览"),
                         toolbox_opts=ToolboxOpts(is_show=True))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
    )
    # 将这个初始图表添加到时间轴中，不关联到任何特定时间点
    timeline.add(all_data_chart, "总览")

    for month_info in unique_months:
        month = month_info['month']
        # 格式化日期
        formatted_month = month.strftime('%Y-%m')
        # 生成特定月份的数据
        data = generate_sunburst_data(month)
        # 创建对应日期的图表
        chart = (
            Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
            .add("", data, radius=[0, "90%"])
            .set_global_opts(title_opts=opts.TitleOpts(title=f"基地部门备件类型分析 - {formatted_month}"),
                             toolbox_opts=ToolboxOpts(is_show=True))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
        )
        # 将图表添加到时间轴
        timeline.add(chart, time_point=formatted_month)
    timeline.add_schema(
        is_auto_play=False,     # 是否自动播放
        is_loop_play=False,     # 是否循环播放
        is_rewind_play=False,   # 是否反向播放
        play_interval=1000,      # 表示播放的速度（跳动的间隔），单位毫秒（ms）
    )

    # 渲染模板
    return render(request, 'itpurchaselist/sunburst_chart.html',
                  context={'chart': timeline.render_embed()})


def generate_chart_option_for_supplier(supplier):
    """
    根据供应商出售的备件类型进行绘制玫瑰图
    """
    # 如果供应商不活跃，则返回None
    if not supplier.is_active:
        return None

    # 计算该供应商销售的每种备件类型的总价
    purchases = Purchase.objects.filter(supplier=supplier)
    spare_parts_totals = purchases.values(
        'spare_part_type__name').annotate(total_price=Sum('total_price'))

    # 为图表准备数据
    data = []
    for spare_part_total in spare_parts_totals:
        # 转换为字符串以避免序列化问题
        data.append({
            'value': str(spare_part_total['total_price']),
            'name': spare_part_total['spare_part_type__name']
        })

    # 创建图表选项
    chart_option = {
        'title': {'text': f"{supplier.name}的备件类型总价分析"},
        'tooltip': {'trigger': 'item', 'formatter': "{a} <br/>{b} : {c} ({d}%)"},
        'series': [
            {
                'name': '销售额',
                'type': 'pie',
                'radius': '55%',
                'center': ['50%', '60%'],
                'data': data,
                'emphasis': {
                    'itemStyle': {
                        'shadowBlur': 10,
                        'shadowOffsetX': 0,
                        'shadowColor': 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }
    return chart_option


def rose_chart(request):
    """
    生成玫瑰图
    """
    suppliers = Supplier.objects.filter(is_active=True)
    charts_html = ""
    for idx, supplier in enumerate(suppliers, start=1):
        chart_option = generate_chart_option_for_supplier(supplier)
        chart_html = f"""
        <div id="chart_{idx}" style="width: 1000px;height:600px;"></div>
        <script type="text/javascript">
            var myChart_{idx} = echarts.init(document.getElementById('chart_{idx}'));
            var option = {json.dumps(chart_option, cls=DjangoJSONEncoder)};
            myChart_{idx}.setOption(option);
        </script>
        """
        charts_html += chart_html
    # 将串联的 HTML 标记为可安全呈现
    charts_html_safe = mark_safe(charts_html)
    return render(request, 'itpurchaselist/rose_chart.html', {'charts_html': charts_html_safe})


def test_view(request):
    """
    测试使用
    """
    suppliers = Supplier.objects.all()
    charts_data = [generate_chart_option_for_supplier(
        supplier) for supplier in suppliers]
    charts_data_json = json.dumps(charts_data, cls=DjangoJSONEncoder)
    print(charts_data_json)
    return HttpResponse("Check the console.")


def ledger_check_view(request):
    """
    处理文件上传并进行格式检查
    """
    context = {}

    if request.method == 'POST':
        file1 = request.FILES.get('file1')
        file2 = request.FILES.get('file2')

        if file1 and file2:
            # 检查文件格式并保存文件
            path1, is_valid1 = save_uploaded_file(file1)
            path2, is_valid2 = save_uploaded_file(file2)

            if not is_valid1 or not is_valid2:
                context['error'] = "上传文件格式错误，请使用 Excel 或 CSV 格式的文件。"
            else:
                try:
                    # 执行比较逻辑
                    comparison_result = compare_excel_files(path1, path2)
                    context['comparison_result'] = comparison_result
                except UnicodeDecodeError:
                    context['error'] = "上传文件格式错误，请使用 CSV 的 utf-8 或 gbk 格式的文件。"

    return render(request, 'itpurchaselist/compare_excel.html', context)


def save_uploaded_file(f):
    """
    上传文件，如果上传格式错误，则不上传
    """
    _, file_extension = os.path.splitext(f.name)
    if file_extension not in ['.xls', '.xlsx', '.csv']:
        return None, False

    current_time = datetime.now().strftime('%Y%m%d_%H%M')
    upload_dir = os.path.join(settings.MEDIA_ROOT, current_time)

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path, True


def compare_excel_files(file1, file2):
    """
    用于两个文件的比较逻辑, 如果同电脑编号下, IP地址或者MAC地址有不同, 则返回不同的值
    """
    # 读取两个Excel文件
    df1 = read_file(file1)
    df2 = read_file(file2)

    # 基于'电脑编号'合并两个DataFrame
    merged_df = pd.merge(df1, df2, on='电脑编号', suffixes=('_1', '_2'))

    # 初始化比较结果列表
    comparison_results = []

    # 遍历合并后的DataFrame
    for index, row in merged_df.iterrows():
        differences = {}
        # 比较IP地址
        if row['IP地址_1'] != row['IP地址_2']:
            differences['IP地址'] = {'表1': row['IP地址_1'], '表2': row['IP地址_2']}

        # 比较MAC地址，移除'-'并忽略大小写
        mac1 = row['MAC地址_1'].replace('-', '').lower()
        mac2 = row['MAC地址_2'].replace('-', '').lower()
        if mac1 != mac2:
            differences['MAC地址'] = {'表1': row['MAC地址_1'], '表2': row['MAC地址_2']}

        # 如果有差异，添加到结果列表
        if differences:
            comparison_results.append({'电脑编号': row['电脑编号'], '差异': differences})

    return comparison_results


def read_file(file_path):
    """
    用于鉴定只上传excel或者csv格式
    """
    _, file_extension = os.path.splitext(file_path)
    if file_extension in ['.xls', '.xlsx']:
        return pd.read_excel(file_path)
    elif file_extension == '.csv':
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # 从dhcp服务器中导出csv文件，编码为gbk
            return pd.read_csv(file_path, encoding='gbk')


@user_passes_test(lambda u: u.is_superuser)
def logs_admin(request):
    # 获取所有日志条目
    logs = LogEntry.objects.select_related(
        'user', 'content_type').order_by('-action_time')

    # 将日志传递到模板
    context = {
        'logs': logs
    }
    return render(request, 'admin/logs.html', context)


def network_status(request):
    devices = NetworkDevice.objects.all()
    devices_status = [(device, cache.get(
        f'network_device_status_{device.pk}', '状态未知')) for device in devices]
    context = {'devices_status': devices_status}
    return render(request, 'itpurchaselist/networkstatus.html', context)


def get_netdevice_status(request):
    # devices = NetworkDevice.objects.all()
    exclude_devices = ['10.11.210.71', '10.11.210.41', '10.11.210.41', '10.11.254.17',
                       '10.11.254.9', '10.11.255.203', '10.10.10.220', '10.10.10.230']  # 排除列表
    devices = NetworkDevice.objects.exclude(ip_address__in=exclude_devices)

    bot = WechatWorkBot(
        webhook_url='https://qyapi.weixin.qq.com/cgi-bin/webhook/*****'
    )  # 实例化机器人，使用您的 webhook URL

    for device in devices:
        status = cache.get(f'network_device_status_{device.pk}', '未知')
        offline_count_key = f'offline_count_{device.pk}'
        offline_count = cache.get(offline_count_key, 0)
        # 如果设备掉线并且掉线次数少于3次
        if status == '未知' and offline_count < 3:
            device_ip = ipaddress.ip_address(device.ip_address)
            rack_position = device.rack_position
            mentioned_list, mentioned_mobile_list, custom_message = determine_notification_details(
                device_ip, status, rack_position)
            if custom_message:
                bot.send_message(custom_message, mentioned_list=mentioned_list,
                                 mentioned_mobile_list=mentioned_mobile_list)
            # 更新掉线次数
            cache.set(offline_count_key, offline_count + 1, timeout=60*60*24)   # 如果长期掉线，那么缓存时间设置1天
            # 如果设备恢复在线，则重置掉线次数
        elif status == '在线':
            cache.set(offline_count_key, 0)

    device_statuses = [
        {
            'id': device.pk,
            'name': device.name,
            'ip_address': device.ip_address,
            'rack_position': device.rack_position,
            'status': cache.get(f'network_device_status_{device.pk}', '未知'),
            'brand': device.brand,
            'type': device.type,
            'model': device.model,
            'serial_number': device.serial_number,
            'purchase_date': device.purchase_date,
            'location': device.location,
            'maintenance_status': device.get_maintenance_status_display(),
            'service_object': device.service_object,
            'purchase_price': device.purchase_price,
            'supplier': device.supplier.name,
            'username': device.username,
            'password': device.password,
            'web_link': device.web_link,
            'remarks': device.remarks,
        }
        for device in devices
    ]
    return JsonResponse(device_statuses, safe=False)


def jump_webssh(request):
    # 将 IP 地址传递到模板中
    ip_address = request.GET.get('ip', '')
    context = {'ip_address': ip_address}
    return render(request, 'itpurchaselist/webssh.html', context)
