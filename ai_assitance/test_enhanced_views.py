"""
Test script to verify the enhanced AI assistance functionality for child growth measurement tracking
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from measurement.models import Child, Measurement, Result
from datetime import date, timedelta
import json

User = get_user_model()

class EnhancedAIAssistanceTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a parent user
        self.parent = User.objects.create_user(
            username='testparent',
            email='parent@test.com',
            fullname='Test Parent',
            password='testpass123',
            role='parent'
        )
        
        # Create a child
        self.child = Child.objects.create(
            name='Test Child',
            date_of_birth=date.today() - timedelta(days=365*2),  # 2 years old
            gender='M',
            parent=self.parent
        )
        
        # Create a measurement
        self.measurement = Measurement.objects.create(
            child=self.child,
            height=85.0,
            weight=12.5
        )
        
        # Create result (will be auto-created by signal, but let's ensure it exists)
        self.result, created = Result.objects.get_or_create(
            measurement=self.measurement,
            defaults={
                'haz': -1.5,
                'is_stunted': False,
                'severity': None,
                'recommendation': 'Child is growing well'
            }
        )
        
        self.client = Client()
        
    def test_child_measurement_context_retrieval(self):
        """Test that child measurement context is properly retrieved"""
        from ai_assitance.views import get_child_measurement_context
        
        context = get_child_measurement_context(self.parent)
        
        self.assertIsNotNone(context)
        self.assertIsInstance(context, list)
        self.assertEqual(len(context), 1)
        
        child_data = context[0]
        self.assertEqual(child_data['name'], 'Test Child')
        self.assertEqual(child_data['height'], 85.0)
        self.assertEqual(child_data['weight'], 12.5)
        self.assertFalse(child_data['is_stunted'])
        
    def test_personalized_prompt_generation(self):
        """Test that personalized prompts are generated correctly"""
        from ai_assitance.views import generate_personalized_prompt, get_child_measurement_context
        
        context = get_child_measurement_context(self.parent)
        prompt = generate_personalized_prompt("What foods should I give my child?", context)
        
        self.assertIn("Test Child", prompt)
        self.assertIn("Height 85.0cm", prompt)
        self.assertIn("normal growth", prompt)
        self.assertIn("nutrition", prompt)
        
    def test_quick_nutrition_advice_endpoint(self):
        """Test the quick nutrition advice API endpoint"""
        self.client.force_login(self.parent)
        
        url = reverse('ai_assitance:quick_nutrition_advice', kwargs={'child_id': self.child.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['child_name'], 'Test Child')
        self.assertIn('current_status', data)
        self.assertIn('quick_recommendations', data)
        self.assertIn('feeding_schedule', data)
        self.assertIn('warning_signs', data)
        self.assertIn('next_steps', data)
        
    def test_growth_insights_endpoint(self):
        """Test the growth insights API endpoint"""
        self.client.force_login(self.parent)
        
        url = reverse('ai_assitance:child_growth_insights', kwargs={'child_id': self.child.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('insights', data)
        self.assertEqual(len(data['insights']), 1)
        
        insight = data['insights'][0]
        self.assertEqual(insight['child_name'], 'Test Child')
        self.assertIn('growth_data', insight)
        self.assertIn('trend_analysis', insight)
        
    def test_nutrition_recommendations_for_stunted_child(self):
        """Test nutrition recommendations for a stunted child"""
        from ai_assitance.views import get_nutrition_recommendations
        
        # Create stunted child data
        stunted_child_data = [{
            'name': 'Stunted Child',
            'age_months': 24,
            'is_stunted': True,
            'severity': 'moderate',
            'haz_score': -2.5
        }]
        
        recommendations = get_nutrition_recommendations(stunted_child_data)
        
        self.assertIn("protein intake", recommendations)
        self.assertIn("frequent meals", recommendations)
        self.assertIn("Stunted Child", recommendations)
        
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access endpoints"""
        url = reverse('ai_assitance:quick_nutrition_advice', kwargs={'child_id': self.child.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 401)
        
    def test_wrong_parent_access(self):
        """Test that parents cannot access other parents' children"""
        # Create another parent
        other_parent = User.objects.create_user(
            username='otherparent',
            email='other@test.com',
            fullname='Other Parent',
            password='testpass123',
            role='parent'
        )
        
        self.client.force_login(other_parent)
        
        url = reverse('ai_assitance:quick_nutrition_advice', kwargs={'child_id': self.child.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    print("Enhanced AI Assistance Test Suite")
    print("Run with: python manage.py test ai_assitance.test_enhanced_views")
