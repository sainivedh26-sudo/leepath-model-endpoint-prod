import json
import os
from recommender import QuestionRecommender
import joblib

def handler(event, context):
    """AWS Lambda handler function for question recommendations"""
    # Handle CORS preflight
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
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event.get('body', '{}'))
        else:
            body = event.get('body', {})
        
        if not body or 'questions' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
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
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
