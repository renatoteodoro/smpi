from django.urls import path

from . import views

app_name = 'assets'
urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='equipment_list'),
    path('create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('<int:pk>/points/create/', views.MeasurementPointCreateView.as_view(), name='measurement_point_create'),
    path('<int:pk>/summarize/', views.request_equipment_summary, name='summarize'),
    path('<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
]
