from django.urls import path

from . import views

app_name = 'faults'
urlpatterns = [
    path('', views.FaultListView.as_view(), name='fault_list'),
    path('create/', views.FaultCreateView.as_view(), name='fault_create'),
    path('<int:pk>/edit/', views.FaultUpdateView.as_view(), name='fault_update'),
]
