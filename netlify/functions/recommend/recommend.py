import json
import os
import joblib
import sys
from recommender import QuestionRecommender

def handler(event, context):
    """
    Netlify function handler for question recommendations
    """
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': ''
        }

    try:
        # Get request body
        body = json.loads(event['body']) if event.get('body') else {}
        
        if not body or 'questions' not in body:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Please provide questions in the request body'
                })
            }
            
        input_questions = body['questions']
        num_recommendations = body.get('num_recommendations', 8)
        
        # Initialize recommender
        try:
            model_path = os.path.join(os.path.dirname(__file__), "model_prod.pkl")
            recommender = joblib.load(model_path)
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': f'Error loading model: {str(e)}'
                })
            }

        # Get recommendations
        predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
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
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e)
            })
        }
