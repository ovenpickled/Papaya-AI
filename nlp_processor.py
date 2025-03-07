import os
from dotenv import load_dotenv
from openai import OpenAI

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
                    {"role": "system", "content": "You are an AI assistant that helps interpret user commands for a Windows PC. Extract the intent and relevant entities from the user's query. Format your response as JSON with 'intent' and 'entities' fields."},
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
            return task_result