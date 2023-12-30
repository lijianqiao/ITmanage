"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITmanage
 @Email: lijianqiao2906@live.com
 @FileName: st.py
 @DateTime: 2023/12/19 12:34
 @Docs:  streamlit 数据处理
"""

import re
import matplotlib
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import plotly.express as px
from statsmodels.formula.api import ols
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sweetviz as sv
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report
from PIL import Image


# 注册中文字体
pdfmetrics.registerFont(TTFont('幼圆', './SIMYOU.TTF'))  # 替换为您的字体文件路径

# 设置 Matplotlib 字体为支持中文的字体
matplotlib.rcParams['font.family'] = 'SimHei'  # 例如设置为 "SimHei"
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题


class DataLoader:
    """
    用于数据加载, 处理上传格式，多工作表判断
    """

    def __init__(self):
        self.df = None
        self.sheets = None

    def upload_file(self):
        """
        创建单个文件上传控件。
        用户可以上传 '.xlsx' 和 '.csv' 格式的文件。
        如果上传了不支持的文件格式，显示错误信息。
        如果没有文件被上传，Streamlit 应用会停止。
        创建一个多选控件，允许用户选择要查看和处理的工作表。
        对于 Excel 文件，显示所有工作表的名称。
        对于 CSV 文件，显示 "Sheet1"。
        如果没有工作表被选择，Streamlit 应用会停止。
        返回: 文件列名
        """
        uploaded_file = st.file_uploader("选择数据文件", type=['xlsx', 'csv'])
        if uploaded_file is None:
            st.stop()
        elif not uploaded_file.name.endswith(('.xlsx', '.csv')):
            st.error("不支持的文件格式。请上传 '.xlsx' 或 '.csv' 格式的文件。")
            st.stop()
        else:
            data = self.load_data(uploaded_file)
            if isinstance(data, dict):  # 如果是字典，则让用户选择工作表
                self.sheets = list(data.keys())
                if self.sheets:  # 确保工作表列表不为空
                    sheets_selected = st.multiselect("选择工作表", self.sheets, default=self.sheets[0])
                    if sheets_selected:  # 确保用户已选择工作表
                        self.df = {sheet: data[sheet] for sheet in sheets_selected}
                        return self.df, sheets_selected
                    else:
                        st.stop()
                else:
                    st.error("未找到任何工作表。")
                    st.stop()
            else:
                self.df = data
                self.sheets = ['Sheet1']
            return self.df, self.sheets

    @st.cache_data(ttl=600, max_entries=100)
    def load_data(_self, uploaded_file):
        """
        根据文件类型读取数据。
        对于 Excel 文件，使用 pd.read_excel。
        对于 CSV 文件，使用 pd.read_csv。
        返回: 对于 Excel 文件包含所有工作表的字典，对于 CSV 文件返回单个 DataFrame。
        """
        if uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file, sheet_name=None)  # 读取 Excel 文件所有工作表
        elif uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)


class AllDataLoader:
    def __init__(self):
        self.df = None

    def upload_file(self):
        uploaded_files = st.file_uploader("上传多个xlsx、csv文件", type=['xlsx', 'csv'], accept_multiple_files=True)
        if not uploaded_files:
            st.stop()
        for uploaded_file in uploaded_files:
            if not uploaded_file.name.endswith(('.xlsx', '.csv')):
                st.error("不支持的文件格式。请上传 '.xlsx' 或 '.csv' 格式的文件。")
                st.stop()
        else:
            self.df = self.load_data(uploaded_files)
        return self.df

    @st.cache_data(ttl=600, max_entries=100)
    def load_data(_self, uploaded_files):
        df_list = []
        # df_list = [pd.read_csv(file) for file in uploaded_files]
        for file in uploaded_files:
            if file.name.endswith('.xlsx'):
                xls = pd.read_excel(file, sheet_name=None)
                for sheet_df in xls.values():
                    df_list.append(sheet_df)
            else:
                df_list.append(pd.read_csv(file))
        df = pd.concat(df_list, ignore_index=True)
        return df


class DataAnalysis:
    """
    用于数据分析
    """

    def __init__(self):
        self.df = None
        self.sheets = None
        self.loader = DataLoader()
        init_streamlit_comm()  # 初始化 Pygwalker 通信

    def build_filters(self, sheet_name, df_col):
        """
        为指定的工作表创建筛选器。
        对于每个对象类型的列，创建一个多选框，让用户选择该列的值进行筛选。
        返回: 应用了筛选条件后的 DataFrame。
        """
        with st.expander('筛选'):
            df = df_col.copy()  # 使用 df_col 的副本进行操作，确保 df 总是有初始值
            filter_options = st.text_input('输入筛选关键词（使用逗号或空格分隔）', key=f'{sheet_name}_filter_input')
            if filter_options:
                filter_keywords = re.split(r'[,\s]+', filter_options)
                df = df[df.apply(
                        lambda x: any(keyword.lower() in str(v).lower() for v in x for keyword in filter_keywords),
                        axis=1)]
            for col in df.columns:
                # 尝试对列进行排序，如果失败，则捕获异常
                try:
                    sorted_values = df[col].drop_duplicates().sort_values()
                except TypeError:
                    # 如果排序失败（可能是因为数据类型混合），则转换为字符串进行排序
                    sorted_values = df[col].astype(str).drop_duplicates().sort_values()
                selected_values = st.multiselect(f"{sheet_name} - {col}", sorted_values, key=f'{sheet_name}_{col}')
                if selected_values:
                    # 这里假设选中的值都是字符串类型，根据选中的字符串进行筛选
                    df = df[df[col].astype(str).isin(selected_values)]
        return df

    @st.cache_resource
    def get_pyg_html(_self, df: pd.DataFrame) -> str:
        """
        使用 Pygwalker 处理给定的 DataFrame 并生成 HTML 代码。
        这是一个缓存的函数，用于防止重复的计算和内存溢出。
        返回: 包含 Pygwalker 处理结果的 HTML 字符串。
        """
        html = get_streamlit_html(df, spec="./gw0.json", use_kernel_calc=True, debug=False)
        return html

    def display_ag_grid(self, df: pd.DataFrame):
        """显示Ag-Grid表格"""
        options = GridOptionsBuilder.from_dataframe(df)
        options.configure_side_bar()
        options.configure_default_column(fit_columns_on_grid_load=True, editable=True, groupable=True,
                                         value=True, enableRowGroup=True, aggFunc="sum")
        options.configure_pagination(
            enabled=False,  # 分页
            paginationAutoPageSize=True,  # 根据网格高度自动设置最佳分页大小
            paginationPageSize=20,  # 强制页面每页包含此行数。 默认为 10
        )
        # 'single'：单个，'multiple'：多个，'disabled'：禁用
        options.configure_selection("multiple", use_checkbox=True,
                                    groupSelectsChildren=True, groupSelectsFiltered=True)

        gridOptions = options.build()
        # 在这里添加一个基于 sheet_name 的唯一 key
        # grid_key = f"ag_grid__{int(time.time())}"
        aggrid = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True,
                        update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED |
                        GridUpdateMode.MODEL_CHANGED, editable=True, reload_data=False,
                        height=600, width="100%", data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                        # 下方滚动条
                        custom_css={
                            "#gridToolBar": {
                                "padding-bottom": "0px !important",
                            }
                        },
                        )
        updated_df = aggrid['data']

        st.dataframe(updated_df)
        return updated_df

    def build_field_selector(self, sheet_name):
        """让用户选择想要展示的字段。"""
        df = self.df[sheet_name] if isinstance(self.df, dict) else self.df  # 获取正确的 DataFrame
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(f"选择 {sheet_name} 工作表的字段", all_columns,
                                          all_columns, key=f'{sheet_name}_field_select')
        return selected_columns

    def build_sheet_tabs(self):
        """
        为每个选定的工作表创建一个标签页。
        在每个标签页中，显示筛选器和 DataFrame，并展示 Pygwalker 的结果。
        """
        tabs = st.tabs(self.sheets)  # 创建标签页组
        for tab, sheet_name in zip(tabs, self.sheets):
            with tab:  # 在对应的标签页下操作
                # df = df_or_dict[sheet_name]
                df = self.df[sheet_name] if isinstance(self.df, dict) else self.df
                selected_columns = self.build_field_selector(sheet_name)
                if not selected_columns:
                    st.error("至少也要选择一个列名吧。 ಥ_ಥ ")
                    continue
                df_col = df[selected_columns]  # 仅保留用户选择的字段
                filtered_df = self.build_filters(sheet_name, df_col)
                update_df = self.display_ag_grid(filtered_df)
                if not update_df.empty and not update_df.columns.empty:
                    pyg_html = self.get_pyg_html(update_df)
                    components.html(pyg_html, height=1000, scrolling=True)
                else:
                    st.error("条件这么苛刻吗？至少也要选择一个列名吧。 (๑¯ิε ¯ิ๑) ")

    def run(self):
        loaded_data = self.loader.upload_file()
        if loaded_data is not None:
            self.df, self.sheets = loaded_data
            if self.df is not None and self.sheets is not None:
                self.build_sheet_tabs()
                st.cache_resource.clear()


class DataProcessing:
    def __init__(self):
        self.df = None
        self.loader = DataLoader()
        self.selected_file = None

    def run(self):
        loaded_data = self.loader.upload_file()
        if loaded_data is not None:
            self.df, _ = loaded_data  # 只需要DataFrame, 不需要sheets
            if self.df is not None:
                self.display_data()

    def select_file(self, loaded_data):
        file_names = list(loaded_data.keys())
        self.selected_file = st.selectbox("选择要分析的文件", file_names)

    def display_data(self):
        """
        使用 ag-grid 显示数据。
        返回: 用户更新的数据。
        """

        if st.checkbox('显示原始数据'):
            st.write(self.df)

        # 描述性统计
        if st.checkbox('显示描述性统计'):
            st.write(self.df.describe())

        if st.checkbox('开始分析'):
            # 字段选择
            options = st.multiselect('选择字段进行分析', self.df.columns, default=self.df.columns[0])
            if options:
                self.display_line_chart(options)

    def display_line_chart(self, options):
        # 创建示例数据
        # 使用选中的字段创建图表
        if self.df is not None:
            fig = px.line(self.df, x=self.df.index, y=options, title='数据分析图表')
            st.plotly_chart(fig)


class AllDataAnalysis:
    def __init__(self):
        self.df = None
        self.loader = AllDataLoader()

    def views_data(self):
        if st.checkbox('显示原始数据'):
            st.write(self.df)

        if st.checkbox('显示描述性统计'):
            st.write(self.df.describe())

    def run(self):
        load_data = self.loader.upload_file()
        if load_data is not None:
            self.df = load_data
            if self.df is not None:
                self.views_data()


class AllDataProcessing:
    def __init__(self):
        self.df = None
        self.loader = AllDataLoader()

    def views_data(self):
        # 数据可视化
        if st.checkbox('matplotlib数据可视化'):
            st.subheader('数据分布')
            select_column = st.selectbox('选择要可视化的列', self.df.columns)
            plt.figure(figsize=(10, 4))
            sns.histplot(self.df[select_column], kde=True)
            st.pyplot(plt.gcf())

        if st.checkbox('plotly数据可视化'):
            st.subheader('Plotly数据可视化')

            # 选择图表类型
            chart_type = st.selectbox(
                "选择图表类型",
                ['直方图', '折线图', '散点图', '条形图', '箱线图', '热力图']
            )
            # 初始化x_axis和y_axis
            x_axis = None
            y_axis = None

            # 根据图表类型选择相应的数据列
            if chart_type in ['直方图', '条形图', '箱线图', '热力图']:
                x_axis = st.selectbox("选择X轴数据列", self.df.columns)
                if chart_type in ['热力图']:
                    y_axis = st.selectbox("选择Y轴数据列", self.df.columns)
            elif chart_type in ['折线图', '散点图']:
                x_axis = st.selectbox("选择X轴数据列", self.df.columns)
                y_axis = st.selectbox("选择Y轴数据列", self.df.columns)

            # 绘制图表
            if chart_type == '直方图':
                fig = px.histogram(self.df, x=x_axis)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == '折线图':
                fig = px.line(self.df, x=x_axis, y=y_axis)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == '散点图':
                fig = px.scatter(self.df, x=x_axis, y=y_axis)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == '条形图':
                fig = px.bar(self.df, x=x_axis)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == '箱线图':
                fig = px.box(self.df, x=x_axis, notched=True)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == '热力图':
                fig = px.density_heatmap(self.df, x=x_axis, y=y_axis, marginal_x="rug", marginal_y="histogram")
                st.plotly_chart(fig, use_container_width=True)

        # 统计分析
        if st.checkbox('statsmodels统计分析'):
            st.subheader('统计分析')

            # 选择变量
            dependent_var = st.selectbox('选择因变量（Y）', self.df.columns)
            independent_vars = st.multiselect('选择自变量（Xs）', self.df.columns)

            if dependent_var and independent_vars:
                if self.df[dependent_var].isnull().any() or self.df[independent_vars].isnull().any().any():
                    st.error("所选变量中存在空值，请处理空值后再进行分析。")
                else:
                    try:
                        formula = f"{dependent_var} ~ " + " + ".join(independent_vars)
                        model = ols(formula, data=self.df).fit()
                        model_summary = model.summary().as_text()
                        st.text(model_summary)

                        if st.button('生成PDF报告'):
                            pdf_file_path = f'./{dependent_var}_regression_report.pdf'
                            c = canvas.Canvas(pdf_file_path, pagesize=letter)
                            c.setFont('幼圆', 12)  # 使用注册的中文字体
                            textobject = c.beginText(40, 750)
                            for line in model_summary.split('\n'):
                                textobject.textLine(line)
                            c.drawText(textobject)
                            c.save()
                            st.success('PDF报告已生成。')
                            st.download_button(
                                label='下载PDF报告',
                                data=open(pdf_file_path, "rb"),
                                file_name=f'{dependent_var}_regression_report.pdf',
                                mime='application/pdf'
                            )
                    except Exception as e:
                        st.error(f"模型拟合过程中出现错误：{e}")

        if st.checkbox('Sweetviz自动分析(只能分析csv格式文件)'):
            # 创建 Sweetviz 报告
            for col in self.df.columns:
                if self.df[col].apply(lambda x: isinstance(x, (int, float, str))).all():
                    # 如果列中的所有数据都是数值或字符串，则跳过
                    continue
                else:
                    # 否则，将该列转换为字符串类型
                    self.df[col] = self.df[col].astype(str)
                # 创建 Sweetviz 报告
            report = sv.analyze(self.df)

            report.show_html()

        if st.checkbox('ydata-profiling自动分析'):
            # 创建 ydata-profiling 报告
            profile = ProfileReport(self.df, explorative=True)

            # 使用 Streamlit 的 st_profile_report 方法显示报告
            st_profile_report(profile)

    def run(self):
        load_data = self.loader.upload_file()
        if load_data is not None:
            self.df = load_data
            if self.df is not None:
                self.views_data()


class Chatgpt:
    """
    ChatGPT 类，用于用户与文本进行交互
    """
    def __init__(self):
        # 初始化时加载数据和配置图片关键字
        self.data, self.questions = self.load_data("/projects/ITmanage/streamlit/train.txt")
        # 关键字与图片路径的映射
        self.keyword_images = {
            "cmd": ["/projects/ITmanage/streamlit/img/cmd_img.png"],
            "已经阻止此应用": ["/projects/ITmanage/streamlit/img/bash_img.png"],
            "网络权限申请": [
                "/projects/ITmanage/streamlit/img/wangluoquanxianshenqing_1.png",
                "/projects/ITmanage/streamlit/img/wangluoquanxianshenqing_2.png",
                "/projects/ITmanage/streamlit/img/wangluoquanxianshenqing_3.png",
                "/projects/ITmanage/streamlit/img/wangluoquanxianshenqing_4.png",
                "/projects/ITmanage/streamlit/img/wangluoquanxianshenqing_5.png",
            ],
            "主机名": [
                "/projects/ITmanage/streamlit/img/hostname_1.png",
                "/projects/ITmanage/streamlit/img/hostname_2.png",
            ],
            "电脑搬迁": [
                "/projects/ITmanage/streamlit/img/diannaobanqian_1.png",
                "/projects/ITmanage/streamlit/img/diannaobanqian_2.png",
                "/projects/ITmanage/streamlit/img/diannaobanqian_3.png",
            ],
            "复印机扫描": [
                "/projects/ITmanage/streamlit/img/scan.png",
            ],
            "右键没反应": [
                "/projects/ITmanage/streamlit/img/right_no_res.jpg"
            ],
            "sccm部署过程日志文件": [
                "/projects/ITmanage/streamlit/img/sccm_log.png"
            ],
            "设计主机双硬盘": [
                "/projects/ITmanage/streamlit/img/sccm_disk_1.png",
                "/projects/ITmanage/streamlit/img/sccm_disk_2.png"
            ],
            "添加输入法": [
                "/projects/ITmanage/streamlit/img/input_1.png",
                "/projects/ITmanage/streamlit/img/input_2.png",
                "/projects/ITmanage/streamlit/img/input_3.png",
            ],
            "word无法创建工作文件": [
                "/projects/ITmanage/streamlit/img/ie_work.png",
            ],
            "软件中心无法看到内容": [
                "/projects/ITmanage/streamlit/img/sccm_nolook_1.png",
                "/projects/ITmanage/streamlit/img/sccm_nolook_2.png",
            ],
            "桌面卡死": [
                "/projects/ITmanage/streamlit/img/desktop_error_1.png",
                "/projects/ITmanage/streamlit/img/desktop_error_2.png",
                "/projects/ITmanage/streamlit/img/desktop_error_3.png",
                "/projects/ITmanage/streamlit/img/desktop_error_4.png",
            ],
            "eweb": [
                "/projects/ITmanage/streamlit/img/eweb_1.png",
                "/projects/ITmanage/streamlit/img/eweb_2.png",
            ],
            "无法打印": [
                "/projects/ITmanage/streamlit/img/no_print.png",
            ]
            # TODO: 添加更多关键字和图片路径
        }

    def load_data(self, file_path):
        """从文件加载问题和答案数据"""
        data = {}
        questions = []
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            current_question = None
            current_answer = ""
            for line in lines:
                if 'question:' in line:
                    # 当遇到新问题时，保存前一个问题及其答案
                    if current_question is not None:
                        data[current_question] = current_answer.strip()
                    current_question = line.split('question:')[-1].strip().lower()
                    questions.append(current_question)
                    current_answer = ""
                elif 'answer:' in line or (current_question and line.strip()):
                    # 连接答案行，并为 Markdown 格式化添加空格和换行符
                    current_answer += line.replace('answer:', '').rstrip() + '  \n'
            # 保存最后一个问题及其答案
            if current_question is not None:
                data[current_question] = current_answer.strip()
            return data, questions

    def find_answer(self, input_question):
        """根据输入的问题寻找答案"""
        input_question = input_question.lower()
        for question, answer in self.data.items():
            if input_question in question:
                return answer, None
        self.record_new_question(input_question)
        return 4004, None
    
    def record_new_question(self, question):
        """将未找到答案的问题记录到文件中"""
        with open("./streamlit/new_questions.txt", "a", encoding='utf-8') as file:
            file.write('question:' + question + '\n')

    def check_and_show_image(self, keyword):
        """检查给定关键字是否有对应的图片，并显示"""
        image_paths = self.keyword_images.get(keyword)
        if image_paths:
            for index, image_path in enumerate(image_paths, start=1):
                image = Image.open(image_path)
                st.image(image, caption=f'图{index}')

    def clean_text(self, text):
        """清洗文本，移除特殊字符"""
        return re.sub(r'[^\w\s]', '', text)

    def run(self):
        """运行函数"""
        st.title('IT支持问答系统')
        input_question = st.text_input('请输入您的问题：')
        if input_question:  # 确保输入框不为空
            cleaned_input = self.clean_text(input_question)
            answer, _ = self.find_answer(input_question)
            # 检查输入是否与某个问题完全匹配（忽略符号）
            if cleaned_input in (self.clean_text(q) for q in self.questions):
                st.text("答案：")
                st.markdown(answer, unsafe_allow_html=True)
                for keyword in self.keyword_images.keys():
                    if keyword in input_question.lower():
                        self.check_and_show_image(keyword)
                        break
            else:
                if len(input_question) >= 2:
                    if answer == 4004:
                        st.error('没找到这个答案，但是我们已经记录了你提出的这个问题哦。 d(ŐдŐ๑)')  # 显示错误提示
                    else:
                        # 显示可能的问题建议
                        matched_questions = [q for q in self.questions if input_question.lower() in q]
                        if matched_questions:
                            st.text("您可能想搜索的是：")
                            for q in matched_questions:
                                if st.button(q):
                                    answer = self.data[q]
                                    st.text("答案：")
                                    st.markdown(answer, unsafe_allow_html=True)
                                    for keyword in self.keyword_images.keys():
                                        if keyword in q:
                                            self.check_and_show_image(keyword)
                                            break
                elif 2 > len(input_question) > 0:
                    # 提示用户输入更多字符
                    st.error('至少要输入2个字符呀！  ಥ_ಥ ')
        else:
            st.text("您可能想搜索的是[单独搜索显示更佳]：")
            # 每行显示3个按钮
            buttons_per_row = 2
            rows = [self.questions[i:i + buttons_per_row] for i in range(0, len(self.questions), buttons_per_row)]
            for row in rows:
                cols = st.columns(buttons_per_row)
                for i, q in enumerate(row):
                    with cols[i]:  # 选择对应的列
                        if st.button(q, key=f"btn_{q}"):  # 给每个按钮一个唯一的key
                            # 显示点击的问题的答案
                            answer = self.data[q]
                            st.text("答案：")
                            st.markdown(answer, unsafe_allow_html=True)
                            # 显示与问题相关的图片
                            for keyword in self.keyword_images.keys():
                                if keyword in q.lower():
                                    self.check_and_show_image(keyword)
                                    break

def main():
    st.sidebar.title("百宝箱")
    analysis_type = st.sidebar.selectbox("你需要它为你做什么：", ("问答", "单表数据处理及分析", "多表数据处理及分析"),
                                         index=0)
    app = None  # 初始化 app 为 None

    if analysis_type == "问答":
        app = Chatgpt()

    elif analysis_type == "单表数据处理及分析":
        data_analysis_type = st.sidebar.selectbox("选择单表数据处理类型：", ("数据分析", "数据处理"), index=0)
        if data_analysis_type == "数据分析":
            # 这里初始化数据处理的类
            st.title('数据文件分析处理')
            app = DataAnalysis()
        elif data_analysis_type == "数据处理":
            st.title('数据文件可视化')
            app = DataProcessing()

    elif analysis_type == "多表数据处理及分析":
        data_analysis_type = st.sidebar.selectbox("选择多表数据处理类型：", ("数据分析", "数据处理"), index=0)
        if data_analysis_type == "数据分析":
            # 这里初始化数据处理的类
            st.title('数据文件分析处理')
            app = AllDataAnalysis()
        elif data_analysis_type == "数据处理":
            st.title('数据文件可视化')
            app = AllDataProcessing()

    # 在这里添加信息框
    st.sidebar.markdown(
        """

        #### 支持开发:
        如果你觉得这个工具对你有帮助, 欢迎支持！

        """,
        unsafe_allow_html=True
    )
    coffee_image_path = './streamlit/img/coffee_nobg.png'
    st.sidebar.image(coffee_image_path)
    st.sidebar.markdown("---")

    if app is not None:
        app.run()


# 创建 DataApp 实例并运行
if __name__ == "__main__":
    st.set_page_config(page_title='百宝箱', layout='wide')
    main()
