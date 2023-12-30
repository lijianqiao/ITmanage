from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('maintenance_report_analysis/', views.maintenance_report_analysis,
         name='maintenance_report_analysis'),
]
