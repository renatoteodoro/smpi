from django.urls import path

from . import views

app_name = 'prescriptions'
urlpatterns = [
    path('', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('trigger/<int:reading_id>/', views.trigger_analysis, name='trigger_analysis'),
    path('<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), name='prescription_delete'),
]
