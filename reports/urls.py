from django.urls import path

from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('create/', views.ReportCreateView.as_view(), name='report_create'),
    path('<int:pk>/download/', views.ReportDownloadView.as_view(), name='report_download'),
]
