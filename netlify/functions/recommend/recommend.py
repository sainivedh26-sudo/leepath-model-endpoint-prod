#!/usr/bin/env python3
import json
import os
import sys
import joblib
from recommender import QuestionRecommender

def main():
    # Read input from command line arguments
    try:
        input_data = json.loads(sys.argv[1])
        event = input_data.get('body', '{}')
        
        if isinstance(event, str):
            event = json.loads(event)
        
        # Initialize recommender
        model_path = os.path.join(os.path.dirname(__file__), "model_prod.pkl")
        recommender = joblib.load(model_path)
        
        # Validate input
        if not event or 'questions' not in event:
            print(json.dumps({
                'error': 'Please provide questions in the request body'
            }))
            sys.exit(1)
            
        input_questions = event['questions']
        num_recommendations = event.get('num_recommendations', 8)
        
        # Get recommendations
        predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
        # Return results
        print(json.dumps({
            'recommended_questions': predictions,
            'input_questions': input_questions,
            'num_recommendations': num_recommendations
        }))
        
    except Exception as e:
        print(json.dumps({
            'error': str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
