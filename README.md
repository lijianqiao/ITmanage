# ITmanage - IT 资产维修管理平台

ITmanage 是一个基于 Django 框架的 IT 资产维修管理系统，它使用 Django 自带的 admin 后台进行定制，提供了资产管理、维修记录、备件类型管理、采购记录、IT 台账核对、网络设备记录等功能。

# 功能特性

- 资产管理：添加、编辑、删除资产记录。
- 维修记录：查看和管理维修历史。
- 备件管理：管理备件类型和备件库存。
- 报表分析：使用 pyecharts 生成维修配件类型的分析图表。
- 采购记录：查看 IT 类采购清单及报表
- 台账核对：IT 台账核对准确性
- 网络设备记录：登记全部网络设备

```textmate
此系统是用于IT类型资产记录，维修登记，供应商管理。
1. 每个资产生成一个二维码，打印二维码贴在资产上
2. 资产管理员可以通过扫描二维码登录之后看到该资产的信息和维修记录
3. 在资产需要维修时，可以让资产管理员或者维修支持部门（例如成都运维组）登记维修记录，选择对应维修供应商来进行维修，维修状态为：维修中
4. 维修供应商在拿到需要维修的资产之后，可以通过扫描该资产上面的二维码进行登录（供应商通用账号），添加需要更换的备件（填写备件型号、SN和质保期），维修之后更新维修记录中的备件和维修状态。
5. 可以生成维修报表，对维修备件类型生成报表，可以分析出什么备件类型维修较多，从而去降低维修
6. 可以对资产和维修记录进行多种格式文件导出，资产管理员只能对本部门的资产和维修记录导出
7. 可以对IT类采购清单记录并生产各部门采购备件类型、各供应商售出备件类型进行报表查询
8. 可以对IT台账进行准确核对，找出差异性
9. 对网络设备进行登记
```

# 项目结构

```textmate
ITmanage：主项目
assets应用：用于资产管理、维修管理、二维码生成、供应商管理、部门管理、资产管理员管理、备件管理
it_purchase_list应用：采购管理、IT台账核对、网络设备管理、实时网络设备状态
ind_pc应用：工控机管理、工控机设备类型管理
百宝箱：问答、单数据处理\分析、多数据处理\分析
```
# 配置说明

- media：目录用于存放动态生成的二维码图片。
- static：目录包含了项目的静态文件，如 CSS、JS 和图片。由 python manage.py collectstatic 生成
- templates：目录用于存放 HTML 模板及报表生成文件。
- logs：目录用于该项目所产生的日志文件
- pub：目录用于各应用Django-import_export导入导出
- streamlit：目录用于构建问答、数据分析、数据处理
- 项目根目录、media和static中的web.config是用于Windows server 搭建iis使用的
- celery：目录用于执行celery脚本，可放于计划任务中
- Documents：目录用于ubuntu系统搭建整个项目的详细过程

# 快速开始

以下是如何在本地环境设置和运行 ITmanage 项目的步骤：

# 环境要求

- Python==3.11.5
- Django==4.2.7
- MySQL==8.1
- mysqlclient==2.2.0
- pyecharts==2.0.4
- django-import-export==3.3.1
- django-simpleui==2023.11.16
- django-session-timeout==0.1.0
- pandas==2.1.2
- celery==5.3.4
- channels==4.0.0
- daphne==4.0.0
- django-auditlog==2.3.0
- django-celery-beat==2.5.0
- django-celery-results==2.5.1
- django-cors-headers==4.3.1
- django-redis==5.4.0
- eventlet==0.33.3
- flower==2.0.1
- matplotlib==3.8.2
- paramiko==3.3.1
- Pillow==10.1.0
- plotly==5.18.0
- pydantic==2.5.2
- pyecharts==2.0.4
- pysnmp==4.4.12
- redis==5.0.1
- qrcode==7.4.2
- seaborn==0.12.2
- statsmodels==0.14.1
- streamlit==1.29.0
- streamlit-aggrid==0.3.4.post3
- streamlit-ydata-profiling==0.2.1
- sweetviz==2.3.1
- tablib==3.5.0
- ydata-profiling==4.6.3
#### 注意
- pyasn1==0.4.8

# 安装步骤

1. 进入项目目录：

```sh
cd ITmanage
```

2. 安装依赖：

```sh
pip install -r requirements.txt
```

3. 创建数据库：

```sh
mysql -uroot -p <password>
```

```sh
create database ITmanage;
```

4. 迁移数据库

```sh
python manage.py makemigrations
python manage.py migrate
```

5. 创建管理员账号：

```sh
python manage.py createsuperuser
```

6. 生成静态文件：

```sh
python manage.py collectstatic
```

7. 运行开发服务器：

```sh
python manage.py runserver
```

访问 http://127.0.0.1:8050 进行管理操作(在 settings.py 中设置地址)。


# 安全性

请确保在生产环境中更新 SECRET_KEY，并调整其他安全相关的设置。

# 开源协议

ITmanage是完全免费和开源的，并根据 [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可证获得许可。

# 致谢

- [Django](https://www.djangoproject.com/)
