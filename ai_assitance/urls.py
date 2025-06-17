from django.urls import path
from . import views

#url-patterns for the ai_assistance app 
app_name = 'ai_assistance'

urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('api/chat/', views.ChatbotApiView.as_view(), name='chatbot_api'),
]
