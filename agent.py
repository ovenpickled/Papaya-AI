from voice_recognition import VoiceRecognizer
from task_executor import TaskExecutor
from nlp_processor import NLPProcessor
from text_to_speech import TextToSpeech
import json

class Agent:
    def __init__(self):
        self.voice_recognizer = VoiceRecognizer()
        self.task_executor = TaskExecutor()
        self.nlp_processor = NLPProcessor()
        self.tts = TextToSpeech()
    
    def process_query(self, query):
        """Process a user query and execute the appropriate task"""
        # Use NLP to understand the query
        nlp_result = self.nlp_processor.process_query(query)
        
        try:
            # Execute the task
            task_result = self.task_executor.execute_task(query)
            
            # Generate a natural language response
            response = self.nlp_processor.generate_response(task_result)
            
            # Speak the response
            self.tts.speak(response)
            
            return response
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.tts.speak(error_msg)
            return error_msg