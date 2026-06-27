from django.urls import path

from . import views

app_name = 'monitoring'
urlpatterns = [
    path('', views.ReadingListView.as_view(), name='reading_list'),
    path('create/', views.ReadingCreateView.as_view(), name='reading_create'),
    path('<int:pk>/', views.ReadingDetailView.as_view(), name='reading_detail'),
    path('<int:pk>/analyse/', views.trigger_analysis, name='trigger_analysis'),
    path('<int:pk>/summarize/', views.request_event_summary, name='summarize'),
]
