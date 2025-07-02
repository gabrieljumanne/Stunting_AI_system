#!/usr/bin/env python
"""
Demo script to showcase the enhanced AI assistance features for child growth measurement tracking.
Run this script to see how the AI provides personalized nutrition advice based on child measurement data.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/i-castorosa-098/Desktop/stunting_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stunting_project.settings')
django.setup()

from ai_assitance.views import (
    get_child_measurement_context, 
    generate_personalized_prompt,
    get_nutrition_recommendations
)

def demo_personalized_context():
    """Demonstrate how child measurement context is retrieved and used"""
    print("=" * 60)
    print("DEMO: Personalized Child Measurement Context")
    print("=" * 60)
    
    # Simulate child measurement data
    sample_child_data = [
        {
            'name': 'Alice',
            'age_months': 18,
            'height': 78.5,
            'weight': 10.2,
            'haz_score': -2.3,
            'is_stunted': True,
            'severity': 'moderate',
            'measurement_date': '2024-06-20'
        },
        {
            'name': 'Bob',
            'age_months': 30,
            'height': 92.1,
            'weight': 13.8,
            'haz_score': -0.5,
            'is_stunted': False,
            'severity': None,
            'measurement_date': '2024-06-22'
        }
    ]
    
    print("Sample Child Data:")
    for child in sample_child_data:
        status = f"stunted ({child['severity']})" if child['is_stunted'] else "normal growth"
        print(f"  • {child['name']} ({child['age_months']} months): "
              f"Height {child['height']}cm, HAZ {child['haz_score']:.1f}, Status: {status}")
    
    print("\nGenerated Nutrition Recommendations:")
    recommendations = get_nutrition_recommendations(sample_child_data)
    print(f"  {recommendations}")
    
    print("\nPersonalized AI Prompt for 'What should I feed my children?':")
    prompt = generate_personalized_prompt("What should I feed my children?", sample_child_data)
    print(f"  {prompt[:200]}...")
    
    return sample_child_data

def demo_nutrition_advice_by_age_and_status():
    """Demonstrate nutrition advice for different age groups and growth statuses"""
    print("\n" + "=" * 60)
    print("DEMO: Age and Status-Specific Nutrition Advice")
    print("=" * 60)
    
    scenarios = [
        {
            'description': '6-month-old with normal growth',
            'data': [{
                'name': 'Baby Emma',
                'age_months': 6,
                'height': 67.0,
                'weight': 7.5,
                'haz_score': 0.2,
                'is_stunted': False,
                'severity': None
            }]
        },
        {
            'description': '12-month-old with moderate stunting',
            'data': [{
                'name': 'Toddler Sam',
                'age_months': 12,
                'height': 72.0,
                'weight': 8.8,
                'haz_score': -2.1,
                'is_stunted': True,
                'severity': 'moderate'
            }]
        },
        {
            'description': '24-month-old with severe stunting',
            'data': [{
                'name': 'Child Maya',
                'age_months': 24,
                'height': 82.0,
                'weight': 10.5,
                'haz_score': -3.2,
                'is_stunted': True,
                'severity': 'Severe'
            }]
        },
        {
            'description': '36-month-old with excellent growth',
            'data': [{
                'name': 'Child Alex',
                'age_months': 36,
                'height': 98.5,
                'weight': 15.2,
                'haz_score': 1.1,
                'is_stunted': False,
                'severity': None
            }]
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['description']}")
        child = scenario['data'][0]
        print(f"  Child: {child['name']}, Height: {child['height']}cm, HAZ: {child['haz_score']}")
        
        recommendations = get_nutrition_recommendations(scenario['data'])
        print(f"  Recommendations: {recommendations}")

def demo_ai_prompt_enhancement():
    """Demonstrate how user prompts are enhanced with child context"""
    print("\n" + "=" * 60)
    print("DEMO: AI Prompt Enhancement")
    print("=" * 60)
    
    # Sample child with concerning growth
    concerning_child = [{
        'name': 'Lily',
        'age_months': 15,
        'height': 74.2,
        'weight': 9.1,
        'haz_score': -2.8,
        'is_stunted': True,
        'severity': 'Severe'
    }]
    
    user_questions = [
        "My child is not eating well",
        "What foods help with growth?",
        "How often should I feed my child?",
        "Is my child's height normal?"
    ]
    
    print("User Questions Enhanced with Child Context:")
    for question in user_questions:
        print(f"\nOriginal Question: '{question}'")
        enhanced_prompt = generate_personalized_prompt(question, concerning_child)
        print(f"Enhanced Prompt: {enhanced_prompt[:150]}...")

def demo_api_response_format():
    """Demonstrate the format of API responses"""
    print("\n" + "=" * 60)
    print("DEMO: API Response Format")
    print("=" * 60)
    
    # Simulate API response structure
    sample_api_response = {
        'child_name': 'Test Child',
        'age': '2 years 0 months',
        'current_status': {
            'height': 85.0,
            'weight': 12.5,
            'haz_score': -1.8,
            'is_stunted': False,
            'severity': None,
            'measurement_date': '2024-06-25'
        },
        'quick_recommendations': [
            'Balanced family meals with adequate portions',
            'Include all food groups daily',
            'Limit sugary drinks and snacks',
            '✅ Maintain current nutrition to prevent stunting'
        ],
        'feeding_schedule': {
            'frequency': '5 times per day',
            'type': 'Family foods + healthy snacks',
            'schedule': [
                '7am: Breakfast',
                '10am: Snack', 
                '12pm: Lunch',
                '3pm: Snack',
                '6pm: Dinner'
            ]
        },
        'warning_signs': [
            'Loss of appetite for more than 2 days',
            'Frequent illness or infections',
            'Unusual tiredness or lethargy'
        ],
        'next_steps': [
            'Continue current nutrition practices',
            'Regular growth monitoring (monthly)',
            'Maintain healthy feeding habits'
        ]
    }
    
    print("Sample Quick Nutrition Advice API Response:")
    print(f"Child: {sample_api_response['child_name']} ({sample_api_response['age']})")
    print(f"Current Status: Height {sample_api_response['current_status']['height']}cm, "
          f"HAZ {sample_api_response['current_status']['haz_score']}")
    print(f"Recommendations: {len(sample_api_response['quick_recommendations'])} items")
    print(f"Feeding Schedule: {sample_api_response['feeding_schedule']['frequency']}")
    print(f"Warning Signs: {len(sample_api_response['warning_signs'])} items to watch")
    print(f"Next Steps: {len(sample_api_response['next_steps'])} recommended actions")

def main():
    """Run all demonstrations"""
    print("Enhanced AI Assistance for Child Growth Measurement Tracking")
    print("Demo Script - Showcasing Personalized Nutrition Advice")
    
    try:
        demo_personalized_context()
        demo_nutrition_advice_by_age_and_status()
        demo_ai_prompt_enhancement()
        demo_api_response_format()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("✓ Personalized child measurement context retrieval")
        print("✓ Age and growth status-specific nutrition recommendations")
        print("✓ AI prompt enhancement with child data")
        print("✓ Comprehensive API response structure")
        print("✓ Support for multiple children per parent")
        print("✓ Stunting severity-based advice escalation")
        
        print("\nAPI Endpoints Available:")
        print("• /ai_assitance/api/chat/ - Enhanced chat with personalized context")
        print("• /ai_assitance/api/nutrition-advice/<child_id>/ - Quick nutrition advice")
        print("• /ai_assitance/api/insights/<child_id>/ - Growth pattern insights")
        
    except Exception as e:
        print(f"Demo error: {str(e)}")
        print("Make sure Django is properly configured and database is accessible.")

if __name__ == '__main__':
    main()
