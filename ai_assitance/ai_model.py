import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
from django.conf import settings

# Global variables for lazy loading
model = None
labels = None
nutrition = None

def load_model_and_data():
    """Lazy load the model, labels, and nutrition data"""
    global model, labels, nutrition
    
    if model is None or labels is None or nutrition is None:
        try:
            # Get the base directory (ai_assitance app directory)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Load model
            model_path = os.path.join(base_dir, 'food_model.h5')
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                print(f"Model loaded successfully from: {model_path}")
            else:
                print(f"Warning: Model file not found at: {model_path}")
                print("Using mock model for development")
                model = "MOCK_MODEL"  # Mock model for development
            
            # Load labels
            labels_path = os.path.join(base_dir, 'labels.txt')
            if os.path.exists(labels_path):
                with open(labels_path) as f:
                    labels = [line.strip() for line in f]
                print(f"Labels loaded successfully from: {labels_path}")
            else:
                print(f"Warning: Labels file not found at: {labels_path}")
                # Fallback labels for development
                labels = ['apple', 'banana', 'rice', 'bread', 'chicken', 'vegetables', 'unknown']
            
            # Load nutrition data
            nutrition_path = os.path.join(base_dir, 'nutrition.json')
            if os.path.exists(nutrition_path):
                with open(nutrition_path) as f:
                    nutrition = json.load(f)
                print(f"Nutrition data loaded successfully from: {nutrition_path}")
            else:
                print(f"Warning: Nutrition file not found at: {nutrition_path}")
                # Fallback nutrition data for development
                nutrition = {
                    'apple': {
                        'status': 'Healthy',
                        'message': 'Apples are rich in fiber and vitamins.',
                        'nutrition_info': {'calories': '52 per 100g', 'fiber': '2.4g'},
                        'recommendations': ['Eat with skin for more fiber', 'Good for snacks']
                    },
                    'unknown': {
                        'status': 'Unknown',
                        'message': 'Food not recognized. Please try a clearer image.',
                        'nutrition_info': {},
                        'recommendations': []
                    }
                }
                
        except Exception as e:
            print(f"Error loading model and data: {str(e)}")
            # Set fallback values
            model = "MOCK_MODEL"
            labels = ['unknown']
            nutrition = {
                'unknown': {
                    'status': 'Error',
                    'message': f'Error loading AI model: {str(e)}',
                    'nutrition_info': {},
                    'recommendations': []
                }
            }

def analyze_food_image(image_file, confidence_threshold=0.5):
    """
    Analyze a food image and return the predicted label, confidence, and nutrition info.
    Args:
        image_file: Django uploaded file object or file path string
        confidence_threshold: Minimum confidence threshold for predictions
    """
    try:
        # Load model and data if not already loaded
        load_model_and_data()
        
        # Check if using mock model (development mode)
        if model == "MOCK_MODEL":
            # Return mock response for development
            import random
            mock_foods = list(nutrition.keys())
            selected_food = random.choice(mock_foods)
            mock_confidence = random.uniform(0.6, 0.95)
            
            nutrition_info = nutrition.get(selected_food, nutrition['unknown'])
            
            return {
                "food": selected_food,
                "confidence": mock_confidence,
                "status": nutrition_info.get("status", "Unknown"),
                "message": f"[MOCK] {nutrition_info.get('message', 'Mock analysis for development')}",
                "nutrition_info": nutrition_info.get("nutrition_info", {}),
                "recommendations": nutrition_info.get("recommendations", [])
            }
        
        # Real model processing
        # Handle different input types (Django file upload vs file path)
        img = Image.open(image_file).convert("RGB").resize((224, 224))
        
        # Preprocess image
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)

        # Make prediction
        prediction = model.predict(img)[0]
        index = int(np.argmax(prediction))
        label = labels[index] if index < len(labels) else 'unknown'
        confidence = float(np.max(prediction))

        # Get nutrition information
        nutrition_info = nutrition.get(label, nutrition.get('unknown', {
            "status": "Unknown",
            "message": "No nutritional data available for this food.",
            "nutrition_info": {},
            "recommendations": []
        }))

        # Build result
        result = {
            "food": label,
            "confidence": confidence,
            "status": nutrition_info.get("status", "Unknown"),
            "message": nutrition_info.get("message", "No data available."),
            "nutrition_info": nutrition_info.get("nutrition_info", {}),
            "recommendations": nutrition_info.get("recommendations", [])
        }

        # Adjust status based on confidence
        if confidence < confidence_threshold:
            result["status"] = "Uncertain"
            result["message"] = f"The model is not confident in this prediction (confidence: {confidence:.1%}). Please try with a clearer image."

        return result

    except Exception as e:
        return {
            "food": None,
            "confidence": 0.0,
            "status": "Error",
            "message": f"Error analyzing image: {str(e)}",
            "nutrition_info": {},
            "recommendations": []
        }
