"""
URL configuration for ITmanage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.views.generic import RedirectView
from assets import views

favicon_view = RedirectView.as_view(
    url='/static/admin/simpleui-x/img/favicon.ico', permanent=True)


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("admin/", my_admin_site.urls),
    path('assets/', include('assets.urls')),
    path('it_purchase_list/', include('it_purchase_list.urls')),
    path('ind_pc/', include('ind_pc.urls')),
    re_path(r'^media/(?P<path>.*)$', static_serve,
            {'document_root': settings.MEDIA_ROOT}, name='media'),
    # 当用户访问 http://10.11.19.12:8050 时，他们会自动被重定向到 http://10.11.19.12:8050/admin。
    path('', lambda request: redirect('admin/', permanent=True)),
    re_path(r'favicon\.ico$', favicon_view),  # 防止网站标签图标404
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
