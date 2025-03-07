import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

class NLPProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def process_query(self, query):
        """Process a natural language query to determine the intent and entities"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that helps interpret user commands for a Windows PC. Extract the intent and relevant entities from the user's query. Format your response as JSON with 'intent' and 'entities' fields. For payment requests, identify the amount, recipient (if any), and description (if any)."},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing query: {e}")
            return None
    
    def generate_response(self, task_result):
        """Generate a natural language response based on the task execution result"""
        try:
            # If task_result is already a string, just return it
            if isinstance(task_result, str):
                return task_result
                
            # Check if it's JSON
            if isinstance(task_result, str) and (task_result.startswith('{') or task_result.startswith('[')):
                try:
                    # Try to parse and format it
                    parsed = json.loads(task_result)
                    if 'intent' in parsed:
                        intent = parsed.get('intent')
                        if intent == 'check_weather' and 'entities' in parsed:
                            location = parsed['entities'].get('location', 'current location')
                            return f"I'll check the weather for {location}."
                        elif intent == 'schedule_event' or intent == 'schedule_appointment':
                            time = parsed['entities'].get('time', 'unspecified time')
                            date = parsed['entities'].get('date', 'today')
                            return f"I'll schedule an event for {time} on {date}."
                        elif intent == 'approve':
                            number = parsed['entities'].get('number', 1)
                            return f"Approving task {number}."
                except:
                    # If parsing fails, return a generic response
                    return "I'm not sure how to respond to that. Could you rephrase your request?"
                    
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Generate a natural and friendly response based on the result of a task execution."},
                    {"role": "user", "content": f"Task result: {task_result}"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble processing that request right now."
