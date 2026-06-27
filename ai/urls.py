from django.urls import path

from . import views

app_name = 'ai'
urlpatterns = [
    path('', views.SessionListView.as_view(), name='session_list'),
    path('new/', views.SessionCreateView.as_view(), name='session_create'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/stream/', views.chat_stream, name='chat_stream'),
    path('chatbot/stream/', views.chatbot_stream, name='chatbot_stream'),
]
