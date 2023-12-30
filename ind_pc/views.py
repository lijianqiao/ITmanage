from django.shortcuts import render
from pyecharts.charts import Pie, Grid
from pyecharts import options as opts
from pyecharts.globals import ThemeType

from .models import IndustrialPC


def create_pie(data_pair, title, center, radius, total_count):
    return (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="800px", height="400px"))
        .add(series_name=title,
             data_pair=data_pair,
             center=center,
             radius=radius,
             label_opts=opts.LabelOpts(position="outside", formatter="{b}: {c} ({d}%)"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{title} - 总数量: {total_count}"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="middle", pos_left="left")
        )
    )


def industrial_pc_stats(request):
    # 数据查询
    queryset = IndustrialPC.objects.all()
    total_count = queryset.count()

    # 创建数据对
    data_hardening = [("已加固", queryset.filter(hardening=True).count()),
                      ("未加固", total_count - queryset.filter(hardening=True).count())]
    data_network = [("已联网", queryset.filter(network_connected=True).count()),
                    ("未联网", total_count - queryset.filter(network_connected=True).count())]
    data_backup = [("已备份", queryset.filter(backed_up=True).count()),
                   ("未备份", total_count - queryset.filter(backed_up=True).count())]
    data_collection = [("已采集数据", queryset.filter(collection_data=True).count()),
                       ("未采集数据", total_count - queryset.filter(collection_data=True).count())]

    # 创建饼图
    pie_hardening = create_pie(data_hardening, "设备加固占比", center=["30%", "45%"],
                               radius=[80, 120], total_count=total_count)
    pie_network = create_pie(data_network, "设备联网占比", center=["50%", "45%"],
                             radius=[80, 120], total_count=total_count)
    pie_backup = create_pie(data_backup, "设备系统备份占比", center=["30%", "45%"],
                            radius=[80, 120], total_count=total_count)
    pie_collection = create_pie(data_collection, "设备数据采集占比", center=["50%", "45%"],
                                radius=[80, 120], total_count=total_count)

    # 使用 render_embed 方法生成 HTML 代码
    pie_hardening_html = pie_hardening.render_embed()
    pie_network_html = pie_network.render_embed()
    pie_backup_html = pie_backup.render_embed()
    pie_collection_html = pie_collection.render_embed()

    # 将图表渲染结果和 JavaScript 依赖传递到模板上下文中
    context = {
        'pie_hardening_html': pie_hardening_html,
        'pie_network_html': pie_network_html,
        'pie_backup_html': pie_backup_html,
        'pie_collection_html': pie_collection_html,
    }

    return render(request, 'ind_pc/industrial_pc_stats.html', context)
