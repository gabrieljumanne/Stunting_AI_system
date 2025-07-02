from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import requests
import json
import logging
from measurement.models import Child, Measurement, Result
from .ai_model import analyze_food_image

# Set up logging
logger = logging.getLogger(__name__)

def get_child_measurement_context(user):
    """Get relevant child measurement data for AI context"""
    try:
        if not user.is_authenticated or user.role != 'parent':
            return None

        # Get all children for this parent
        children = Child.objects.filter(parent=user)
        if not children.exists():
            return "No children registered yet. Please register a child first to get personalized advice."

        context_data = []
        for child in children:
            # Get latest measurement
            latest_measurement = Measurement.objects.filter(child=child).order_by('-date').first()
            if latest_measurement:
                try:
                    result = Result.objects.get(measurement=latest_measurement)
                    child_info = {
                        'name': child.name,
                        'age_months': latest_measurement.age_months,
                        'height': latest_measurement.height,
                        'weight': latest_measurement.weight,
                        'haz_score': result.haz,
                        'is_stunted': result.is_stunted,
                        'severity': result.severity,
                        'measurement_date': latest_measurement.date.strftime('%Y-%m-%d')
                    }
                    context_data.append(child_info)
                except Result.DoesNotExist:
                    continue

        return context_data
    except Exception as e:
        logger.error(f"Error getting child measurement context: {str(e)}")
        return None

def get_nutrition_recommendations(child_data):
    """Generate specific nutrition recommendations based on child's growth status"""
    recommendations = []

    for child in child_data:
        age_months = child['age_months']
        is_stunted = child['is_stunted']
        severity = child['severity']
        haz_score = child['haz_score']

        # Age-specific recommendations
        if age_months < 6:
            base_rec = "Exclusive breastfeeding"
        elif age_months < 24:
            base_rec = "Continued breastfeeding with complementary foods"
        else:
            base_rec = "Balanced family foods with adequate portions"

        # Stunting-specific recommendations
        if is_stunted:
            if severity == 'Severe':
                specific_rec = ("URGENT: High-protein foods (eggs, fish, beans), "
                              "fortified cereals, frequent small meals (6-8 times daily), "
                              "immediate medical consultation")
            else:  # Moderate
                specific_rec = ("Increase protein intake (meat, eggs, dairy), "
                              "iron-rich foods (dark leafy greens), "
                              "frequent meals (5-6 times daily)")
        else:
            if haz_score > 0:
                specific_rec = "Continue current nutrition practices, maintain variety"
            else:
                specific_rec = ("Prevent stunting: ensure adequate protein, "
                              "fruits and vegetables, regular meal times")

        recommendations.append(f"{child['name']}: {base_rec}. {specific_rec}")

    return "; ".join(recommendations)

def generate_personalized_prompt(user_prompt, child_context):
    """Generate a personalized prompt based on child measurement data"""
    if not child_context:
        return f"As a child nutrition expert, provide brief advice about: {user_prompt}"

    if isinstance(child_context, str):  # No children case
        return f"As a child nutrition expert, {child_context} For general guidance about: {user_prompt}"

    # Build context from child data
    context_parts = []
    for child in child_context:
        age_years = child['age_months'] // 12
        age_months_remainder = child['age_months'] % 12

        status = "normal growth" if not child['is_stunted'] else f"stunted ({child['severity']})"
        context_parts.append(
            f"Child {child['name']} ({age_years}y {age_months_remainder}m): "
            f"Height {child['height']}cm, HAZ score {child['haz_score']:.2f}, "
            f"Status: {status}"
        )

    context_str = "; ".join(context_parts)

    # Add specific nutrition recommendations
    nutrition_recs = get_nutrition_recommendations(child_context)

    return (f"As a child nutrition expert, considering these children's data: {context_str}. "
            f"Current recommendations: {nutrition_recs}. "
            f"Now provide specific, actionable advice about: {user_prompt}. "
            f"Focus on practical nutrition and growth recommendations.")

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

            # Get child measurement context for personalized responses
            child_context = get_child_measurement_context(request.user)
            logger.info(f"Child context retrieved: {bool(child_context)}")

            # Generate personalized prompt
            personalized_prompt = generate_personalized_prompt(user_prompt, child_context)
            
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
            
            # Enhanced payload with personalized context for child growth tracking
            payload = {
                "model": "google/gemma-3n-e4b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": ("You are a specialized child nutrition and growth expert. "
                                  "Provide evidence-based advice focusing on stunting prevention, "
                                  "proper nutrition for children, and growth monitoring. "
                                  "Always give practical, actionable recommendations. "
                                  "Keep responses concise but comprehensive.")
                    },
                    {
                        "role": "user",
                        "content": f"{personalized_prompt}. Respond in a clear, supportive manner with specific recommendations (maximum 200 words)."
                    }
                ],
                "max_tokens": 300,  # Increased for more detailed advice
                "temperature": 0.6,  # More focused responses
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

            # Enhanced response processing for child growth tracking
            if len(assistance_message) > 1200:
                assistance_message = assistance_message[:1200] + "..."

            # Add context-aware footer if child data was used
            if child_context and isinstance(child_context, list):
                assistance_message += "\n\n💡 This advice is personalized based on your child's current measurements."

            logger.info("Successfully extracted and enhanced assistant message")

            # Return enhanced response with metadata
            response_data = {
                'response': assistance_message,
                'has_child_context': bool(child_context and isinstance(child_context, list)),
                'children_count': len(child_context) if isinstance(child_context, list) else 0
            }

            return Response(response_data, status=status.HTTP_200_OK)
            
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


class ChildGrowthInsightsView(APIView):
    """API endpoint to get AI-generated insights about child growth patterns"""
    permission_classes = [AllowAny]

    def get(self, request, child_id=None):
        try:
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

            if request.user.role != 'parent':
                return Response({'error': 'Only parents can access child insights'}, status=status.HTTP_403_FORBIDDEN)

            # Get specific child or all children
            if child_id:
                try:
                    child = Child.objects.get(id=child_id, parent=request.user)
                    children = [child]
                except Child.DoesNotExist:
                    return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                children = Child.objects.filter(parent=request.user)

            if not children:
                return Response({'error': 'No children found'}, status=status.HTTP_404_NOT_FOUND)

            insights = []
            for child in children:
                # Get measurement history
                measurements = Measurement.objects.filter(child=child).order_by('-date')[:5]  # Last 5 measurements

                if not measurements.exists():
                    continue

                # Analyze growth pattern
                growth_data = []
                for measurement in measurements:
                    try:
                        result = Result.objects.get(measurement=measurement)
                        growth_data.append({
                            'date': measurement.date,
                            'height': measurement.height,
                            'weight': measurement.weight,
                            'age_months': measurement.age_months,
                            'haz': result.haz,
                            'is_stunted': result.is_stunted
                        })
                    except Result.DoesNotExist:
                        continue

                if growth_data:
                    # Generate AI insights prompt
                    latest = growth_data[0]
                    trend_analysis = self._analyze_growth_trend(growth_data)

                    insight_prompt = (
                        f"Analyze growth pattern for {child.name} "
                        f"({latest['age_months']} months old): "
                        f"Latest height {latest['height']}cm, HAZ score {latest['haz']:.2f}. "
                        f"Growth trend: {trend_analysis}. "
                        f"Provide specific nutritional recommendations and next steps."
                    )

                    insights.append({
                        'child_id': child.id,
                        'child_name': child.name,
                        'growth_data': growth_data,
                        'trend_analysis': trend_analysis,
                        'ai_prompt': insight_prompt
                    })

            return Response({'insights': insights}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating child insights: {str(e)}")
            return Response({'error': 'Failed to generate insights'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _analyze_growth_trend(self, growth_data):
        """Analyze growth trend from measurement data"""
        if len(growth_data) < 2:
            return "Insufficient data for trend analysis"

        # Sort by date (oldest first)
        sorted_data = sorted(growth_data, key=lambda x: x['date'])

        # Calculate height velocity
        height_changes = []
        for i in range(1, len(sorted_data)):
            prev = sorted_data[i-1]
            curr = sorted_data[i]

            # Calculate months between measurements
            months_diff = curr['age_months'] - prev['age_months']
            if months_diff > 0:
                height_change = curr['height'] - prev['height']
                height_velocity = height_change / months_diff  # cm per month
                height_changes.append(height_velocity)

        if not height_changes:
            return "Unable to calculate growth velocity"

        avg_velocity = sum(height_changes) / len(height_changes)

        # Analyze HAZ trend
        haz_values = [data['haz'] for data in sorted_data]
        haz_trend = "improving" if haz_values[-1] > haz_values[0] else "declining" if haz_values[-1] < haz_values[0] else "stable"

        # Determine overall trend
        if avg_velocity > 0.5:  # Good growth velocity
            if haz_trend == "improving":
                return "Positive growth trend with improving nutritional status"
            elif haz_trend == "stable":
                return "Steady growth with stable nutritional status"
            else:
                return "Growing but nutritional status needs attention"
        elif avg_velocity > 0.2:
            return f"Moderate growth rate, nutritional status {haz_trend}"
        else:
            return f"Slow growth rate, nutritional status {haz_trend} - requires intervention"


class QuickNutritionAdviceView(APIView):
    """Provide quick nutrition advice based on child's latest measurement"""
    permission_classes = [AllowAny]

    def get(self, request, child_id):
        try:
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

            if request.user.role != 'parent':
                return Response({'error': 'Only parents can access nutrition advice'}, status=status.HTTP_403_FORBIDDEN)

            try:
                child = Child.objects.get(id=child_id, parent=request.user)
            except Child.DoesNotExist:
                return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get latest measurement
            latest_measurement = Measurement.objects.filter(child=child).order_by('-date').first()
            if not latest_measurement:
                return Response({'error': 'No measurements found for this child'}, status=status.HTTP_404_NOT_FOUND)

            try:
                result = Result.objects.get(measurement=latest_measurement)
            except Result.DoesNotExist:
                return Response({'error': 'No results found for latest measurement'}, status=status.HTTP_404_NOT_FOUND)

            # Generate quick advice
            age_months = latest_measurement.age_months
            age_years = age_months // 12
            age_months_remainder = age_months % 12

            advice = {
                'child_name': child.name,
                'age': f"{age_years} years {age_months_remainder} months",
                'current_status': {
                    'height': latest_measurement.height,
                    'weight': latest_measurement.weight,
                    'haz_score': round(result.haz, 2),
                    'is_stunted': result.is_stunted,
                    'severity': result.severity,
                    'measurement_date': latest_measurement.date.strftime('%Y-%m-%d')
                },
                'quick_recommendations': self._get_quick_recommendations(age_months, result),
                'feeding_schedule': self._get_feeding_schedule(age_months),
                'warning_signs': self._get_warning_signs(result),
                'next_steps': self._get_next_steps(result, age_months)
            }

            return Response(advice, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating quick nutrition advice: {str(e)}")
            return Response({'error': 'Failed to generate advice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_quick_recommendations(self, age_months, result):
        """Get quick nutrition recommendations based on age and growth status"""
        recommendations = []

        # Age-based recommendations
        if age_months < 6:
            recommendations.append("Continue exclusive breastfeeding")
            recommendations.append("Ensure frequent feeding (8-12 times per day)")
        elif age_months < 12:
            recommendations.append("Continue breastfeeding + complementary foods")
            recommendations.append("Start with iron-rich foods (fortified cereals, pureed meats)")
            recommendations.append("Introduce variety gradually")
        elif age_months < 24:
            recommendations.append("Continue breastfeeding + family foods")
            recommendations.append("Ensure 3 meals + 2-3 healthy snacks daily")
            recommendations.append("Include protein at every meal")
        else:
            recommendations.append("Balanced family meals with adequate portions")
            recommendations.append("Include all food groups daily")
            recommendations.append("Limit sugary drinks and snacks")

        # Growth status specific recommendations
        if result.is_stunted:
            if result.severity == 'Severe':
                recommendations.extend([
                    "🚨 URGENT: Increase meal frequency to 6-8 times daily",
                    "Add high-protein foods: eggs, fish, beans, dairy",
                    "Consider fortified foods or supplements",
                    "Consult healthcare provider immediately"
                ])
            else:  # Moderate
                recommendations.extend([
                    "⚠️ Increase protein-rich foods in diet",
                    "Add healthy fats: avocado, nuts, oils",
                    "Ensure 5-6 meals/snacks per day",
                    "Monitor growth closely"
                ])
        else:
            if result.haz < -1:
                recommendations.append("✅ Maintain current nutrition to prevent stunting")
            else:
                recommendations.append("✅ Excellent growth - continue current practices")

        return recommendations

    def _get_feeding_schedule(self, age_months):
        """Get age-appropriate feeding schedule"""
        if age_months < 6:
            return {
                'frequency': '8-12 times per day',
                'type': 'Breast milk only',
                'notes': 'On-demand feeding recommended'
            }
        elif age_months < 12:
            return {
                'frequency': '5-6 times per day',
                'type': 'Breast milk + complementary foods',
                'schedule': ['6am: Breast milk', '8am: Breakfast', '10am: Snack',
                           '12pm: Lunch', '3pm: Snack', '6pm: Dinner', '8pm: Breast milk']
            }
        elif age_months < 24:
            return {
                'frequency': '5-6 times per day',
                'type': 'Breast milk + family foods',
                'schedule': ['7am: Breakfast', '10am: Snack', '12pm: Lunch',
                           '3pm: Snack', '6pm: Dinner', '8pm: Breast milk']
            }
        else:
            return {
                'frequency': '5 times per day',
                'type': 'Family foods + healthy snacks',
                'schedule': ['7am: Breakfast', '10am: Snack', '12pm: Lunch',
                           '3pm: Snack', '6pm: Dinner']
            }

    def _get_warning_signs(self, result):
        """Get warning signs to watch for"""
        signs = [
            "Loss of appetite for more than 2 days",
            "Frequent illness or infections",
            "Unusual tiredness or lethargy",
            "Delayed developmental milestones"
        ]

        if result.is_stunted:
            signs.extend([
                "Further height loss or no growth",
                "Severe weight loss",
                "Signs of malnutrition (hair changes, skin problems)"
            ])

        return signs

    def _get_next_steps(self, result, age_months):
        """Get recommended next steps"""
        steps = []

        if result.is_stunted:
            if result.severity == 'Severe':
                steps.extend([
                    "Schedule immediate medical consultation",
                    "Consider nutritional assessment by dietitian",
                    "Follow up measurement in 2-4 weeks"
                ])
            else:
                steps.extend([
                    "Implement nutrition recommendations",
                    "Schedule follow-up in 4-6 weeks",
                    "Monitor for improvement"
                ])
        else:
            steps.extend([
                "Continue current nutrition practices",
                "Regular growth monitoring (monthly if under 2 years, every 3 months if older)",
                "Maintain healthy feeding habits"
            ])

        # Age-specific next steps
        if age_months == 6:
            steps.append("Start introducing complementary foods")
        elif age_months == 12:
            steps.append("Transition to more family foods")
        elif age_months == 24:
            steps.append("Focus on establishing healthy eating patterns")

        return steps


class ChildInsightsPageView(TemplateView):
    """Template view to display the child insights page"""
    template_name = 'ai_assitance/child_insights.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Child Growth Insights'
        return context


class NutritionAdvicePageView(TemplateView):
    """Template view to display the standalone nutrition advice page"""
    template_name = 'ai_assitance/nutrition_advice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nutrition Advice'
        context['child_id'] = self.kwargs['child_id']
        return context


class FoodAnalysisPageView(TemplateView):
    """Template view to display the food analysis page"""
    template_name = 'ai_assitance/food_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Food Image Analysis'
        return context


class FoodImageAnalysisView(APIView):
    """API endpoint to analyze food images and return nutrition information"""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            logger.info("FoodImageAnalysisView POST request received")

            # Check if image file is provided
            if 'image' not in request.FILES:
                logger.warning("No image file provided in request")
                return Response({
                    'error': 'No image file provided',
                    'message': 'Please upload an image file'
                }, status=status.HTTP_400_BAD_REQUEST)

            image_file = request.FILES['image']
            
            # Validate image file
            if not image_file.content_type.startswith('image/'):
                logger.warning(f"Invalid file type: {image_file.content_type}")
                return Response({
                    'error': 'Invalid file type',
                    'message': 'Please upload a valid image file (JPEG, PNG, etc.)'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check file size (limit to 10MB)
            if image_file.size > 10 * 1024 * 1024:
                logger.warning(f"File too large: {image_file.size} bytes")
                return Response({
                    'error': 'File too large',
                    'message': 'Image file must be smaller than 10MB'
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Processing image: {image_file.name}, size: {image_file.size} bytes")

            # Call the AI model function to analyze the image
            try:
                analysis_result = analyze_food_image(image_file)
                logger.info("Food image analysis completed successfully")
                
                # Check if analysis was successful
                if not analysis_result:
                    logger.error("analyze_food_image returned None or empty result")
                    return Response({
                        'error': 'Analysis failed',
                        'message': 'Unable to analyze the food image. Please try again with a clearer image.',
                        'food': None,
                        'status': 'error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Check if there was an error in the analysis
                if analysis_result.get('status') == 'Error':
                    logger.error(f"AI model error: {analysis_result.get('message')}")
                    return Response({
                        'error': 'Model unavailable',
                        'message': 'Food analysis service is currently unavailable. Please try again later.',
                        'food': None,
                        'status': 'error',
                        'details': analysis_result.get('message')
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                # Extract the required fields from the analysis result
                response_data = {
                    'food': analysis_result.get('food', 'Unknown food'),
                    'status': analysis_result.get('status', 'unknown'),
                    'message': analysis_result.get('message', 'Food analysis completed'),
                    'confidence': analysis_result.get('confidence', 0.0),
                    'nutrition_info': analysis_result.get('nutrition_info', {}),
                    'recommendations': analysis_result.get('recommendations', [])
                }

                # Add success indicator
                if response_data['status'] == 'success' or response_data['confidence'] > 0.5:
                    response_data['analysis_successful'] = True
                    logger.info(f"Food identified: {response_data['food']} with confidence: {response_data['confidence']}")
                else:
                    response_data['analysis_successful'] = False
                    logger.warning(f"Low confidence analysis: {response_data['confidence']}")

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Error in analyze_food_image: {str(e)}", exc_info=True)
                return Response({
                    'error': 'Image analysis failed',
                    'message': f'Error analyzing food image: {str(e)}',
                    'food': None,
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Unexpected error in FoodImageAnalysisView: {str(e)}", exc_info=True)
            return Response({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred while processing your image',
                'food': None,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """GET method to provide API information"""
        return Response({
            'message': 'Food Image Analysis API',
            'usage': 'POST an image file to analyze food content',
            'supported_formats': ['JPEG', 'PNG', 'GIF', 'BMP'],
            'max_file_size': '10MB',
            'required_fields': ['image'],
            'response_fields': ['food', 'status', 'message', 'confidence', 'nutrition_info', 'recommendations']
        }, status=status.HTTP_200_OK)