from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings 
import requests


# testmy modals 

class ChatbotApiView(APIView):

    def post(self, request):
        user_prompt = request.data.get('message')
        #validation of user message 
        if not user_prompt:
            return Response({'error':'No message provided, please provide the message !'}, status=status.HTTP_400_BAD_REQUEST)
        
        headers = {
            'Content-type':'application/json',
            'Authorization':f'Bearer {settings.OPEN_ROUTER_KEY}'
            
        }
        
        data = {
            'model':'deepseek/deepseek-chat-v3-0324:free', 
            'messages':[
                {'role':'system', 'content':'You are helpfull assistance specializing in child health and stunting prevention and blanced food preparation'}, 
                {'role':'user', 'content':user_prompt}
            ]
        }
        
        try:
            #try-making the api-request to the open-router server 
            response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            assistance_message = result['choices'][0]['message']['content'] 
            return Response({'response':assistance_message}, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
        
        
  
  
class ChatView(TemplateView):
    """user chat interface display"""
    
    template_name = 'ai_assitance/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #custom context 
        return context