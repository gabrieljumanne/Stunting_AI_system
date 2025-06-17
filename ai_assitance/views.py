from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings 
import requests
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Frontend View - Renders the chat interface
class ChatView(TemplateView):
    template_name = 'ai_assitance/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Assistant for Child Nutrition'
        return context

# API View - Handles the actual AI requests
class ChatbotApiView(APIView):
    permission_classes = [AllowAny]  # Allow testing without authentication

    def post(self, request):
        try:
            logger.info("ChatbotApiView POST request received")
            
            # Get and validate user message
            user_prompt = request.data.get('message')
            logger.info(f"User prompt: {user_prompt}")
            
            if not user_prompt:
                logger.warning("No message provided in request")
                return Response({'error':'No message provided, please provide the message!'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if API key exists
            if not hasattr(settings, 'OPEN_ROUTER_KEY') or not settings.OPEN_ROUTER_KEY:
                logger.error("OPEN_ROUTER_KEY not found in settings")
                return Response({'error': 'API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info("Preparing API request to OpenRouter")
            
            headers = {
                "Authorization": f"Bearer {settings.OPEN_ROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",  
                "X-Title": "Stunting Project AI Assistant",  
            }
            
            # Modified payload for shorter, focused responses
            payload = {
                "model": "google/gemma-3n-e4b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Wewe ni mtaalamu wa lishe kwa watoto. Give a brief, clear answer (maximum 150 words) about: {user_prompt}. ."
                    }
                ],
                "max_tokens": 200,  # Limit response length
                "temperature": 0.7,  # Make responses more focused
                "top_p": 0.9  # Improve response quality
            }
            
            logger.info(f"Sending request to OpenRouter with model: {payload['model']}")
            
            # Make the API request
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            logger.info(f"OpenRouter response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return Response({
                    'error': f'API request failed: {response.status_code}',
                    'detail': response.text,
                    'model_used': payload['model']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Parse the response
            result = response.json()
            logger.info("Successfully received response from OpenRouter")
            
            # Extract the assistant's message
            if 'choices' not in result or len(result['choices']) == 0:
                logger.error(f"Unexpected response format: {result}")
                return Response({'error': 'Unexpected API response format'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            assistance_message = result['choices'][0]['message']['content'].strip()
            
            # Additional truncation if still too long
            if len(assistance_message) > 800:
                assistance_message = assistance_message[:800] + "..."
            
            logger.info("Successfully extracted assistant message")
            
            return Response({'response': assistance_message}, status=status.HTTP_200_OK)
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {str(e)}")
            return Response({'error': 'Request timeout. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return Response({'error': f'API request failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except KeyError as e:
            logger.error(f"KeyError in response parsing: {str(e)}")
            return Response({'error': f'Unexpected API response format: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return Response({'error': 'Invalid JSON response from API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)