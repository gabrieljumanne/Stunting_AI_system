from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings 
import requests
import json


# testmy modals 

class ChatbotApiView(APIView):
    permission_classes = [AllowAny]  # Allow testing without authentication

    def post(self, request):
        user_prompt = request.data.get('message')
        #validation of user message 
        if not user_prompt:
            return Response({'error':'No message provided, please provide the message !'}, status=status.HTTP_400_BAD_REQUEST)
        
        headers = {
            "Authorization": f"Bearer {settings.OPEN_ROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  
            "X-Title": "Stunting Project AI Assistant",  
        }
        
        # Option 1: Remove system message for gemma model
        payload = {
            "model": "google/gemma-3n-e4b-it:free",
            "messages": [
                {
                    "role": "user",
                    "content": f"JE TUNAWEZA KUONGELEA UDUMAVU KWA WATOTO NA LISHE KWA UJUMLA (CHILD STUNTING AND NUTRITION),  {user_prompt}"
                }
            ]
        }
        
        # Option 2: Use a different model that supports system messages
        # payload = {
        #     "model": "meta-llama/llama-3.2-3b-instruct:free",
        #     "messages": [
        #         {
        #             "role": "system", 
        #             "content": "You are a helpful assistant specializing in child health and stunting prevention and balanced food preparation"
        #         },
        #         {
        #             "role": "user",
        #             "content": user_prompt
        #         }
        #     ]
        # }
        
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Better error handling
            if response.status_code != 200:
                return Response({
                    'error': f'API request failed: {response.status_code}',
                    'detail': response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            result = response.json()
            assistance_message = result['choices'][0]['message']['content'] 
            return Response({'response': assistance_message}, status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'API request failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return Response({'error': f'Unexpected API response format: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
        
        
  
  
class ChatView(TemplateView):
    """user chat interface display"""
    
    template_name = 'ai_assitance/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #custom context 
        return context