from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import joblib
from recommender import QuestionRecommender

# Adjust the path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Load the model
try:
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "model_prod.pkl")
    with open(model_path, "rb") as model_file:
        recommender = joblib.load(model_file)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    recommender = None

def handler(event, context):
    # Parse the incoming request body
    try:
        body = json.loads(event['body'])
        
        if not body or 'questions' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Please provide questions in the request body'
                })
            }
            
        input_questions = body['questions']
        num_recommendations = body.get('num_recommendations', 8)
        
        # Validate input
        if not isinstance(input_questions, list):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Questions should be provided as a list'
                })
            }
        
        # Make predictions
        predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
        # Return results
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({
                'recommended_questions': predictions,
                'input_questions': input_questions,
                'num_recommendations': num_recommendations
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
