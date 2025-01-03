import json
import os
import requests
import tempfile
from recommender import QuestionRecommender
import joblib

MODEL_URL = "https://storage.googleapis.com/model-host/model_prod.pkl"

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
        
        # Download and load model
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                print("Downloading model from GCS...")
                response = requests.get(MODEL_URL, stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_file.flush()
                
                print("Loading model...")
                recommender = joblib.load(tmp_file.name)

            # Clean up temporary file
            os.unlink(tmp_file.name)
            
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
        print("Getting recommendations...")
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
