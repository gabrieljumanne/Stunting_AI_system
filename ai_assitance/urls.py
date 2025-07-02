from django.urls import path
from . import views

app_name = 'ai_assitance'

urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('api/chat/', views.ChatbotApiView.as_view(), name='chatbot_api'),
    path('food-analysis/', views.FoodAnalysisPageView.as_view(), name='food_analysis_page'),
    path('api/analyze-food/', views.FoodImageAnalysisView.as_view(), name='food_image_analysis'),
    path('insights/', views.ChildGrowthInsightsView.as_view(), name='growth_insights'),
    path('insights/<int:child_id>/', views.ChildGrowthInsightsView.as_view(), name='child_growth_insights'),
    path('nutrition-advice/<int:child_id>/', views.QuickNutritionAdviceView.as_view(), name='quick_nutrition_advice'),
    path('child-insights/', views.ChildInsightsPageView.as_view(), name='child_insights_page'),
    path('nutrition-page/<int:child_id>/', views.NutritionAdvicePageView.as_view(), name='nutrition_advice_page'),
]