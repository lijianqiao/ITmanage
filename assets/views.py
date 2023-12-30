from django.db.models import Count
from django.shortcuts import render
from pyecharts.options import ToolboxOpts
from pyecharts import options as opts
from pyecharts.charts import Pie

from .models import MaintenanceRecord


def maintenance_report_analysis(request):
    # 获取所有维修记录中使用的备件类型及其数量
    parts_count = (
        MaintenanceRecord.objects
        .exclude(spare_parts__isnull=True)  # 排除备件类型为空的记录
        # 排除维修状态为'维修中'和'已送至供应商'的记录
        .exclude(repair_status__in=['repairing', 'arrived'])
        # 假设在SparePart中有一个名为type的ForeignKey到SparePartType
        .values('spare_parts__type__name')
        .annotate(total=Count('spare_parts'))
        .order_by('-total')
    )

    # 格式化数据以适用于pyecharts
    # 如果没有维修记录，设置data为None
    if not parts_count:
        data = None
        tooltip_text = "无数据"
    else:
        # 格式化数据以适用于pyecharts
        data = [(item['spare_parts__type__name'], item['total'])
                for item in parts_count]
        tooltip_text = "{b}: {c}"

    pei_chat = (
        Pie()
        .add(
            "维修备件类型",
            data if data else [("无数据", 0)],  # 如果没有数据，添加一条信息
            radius=["30%", "75%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=True),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="资产维修配件类型分析"),
            toolbox_opts=ToolboxOpts(is_show=True),
        ).set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}")
        )
    )
    chart_html = pei_chat.render_embed()

    context = {
        'chart_html': chart_html,
    }

    return render(request, 'assets/maintenance_report_analysis.html', context)
