from django.urls import path
from .views import ChatbotApiView, ChatView

app_name = 'ai_assitance'

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('api/chat/', ChatbotApiView.as_view(), name='chat_api')
]
