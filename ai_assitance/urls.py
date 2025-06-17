from django.urls import path
from . import views

app_name = 'ai_assitance'

urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('api/chat/', views.ChatbotApiView.as_view(), name='chatbot_api'),
]