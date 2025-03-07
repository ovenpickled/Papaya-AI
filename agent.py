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
        # Check for direct commands that should bypass NLP processing
        lower_query = query.lower()
        
        # Direct command patterns
        direct_commands = [
            "open", "switch", "set alarm", "set a alarm", "set an alarm", "weather"
        ]
        
        # Check if this is a direct command
        is_direct_command = any(command in lower_query for command in direct_commands)
        
        if is_direct_command:
            # Execute the task directly
            print(f"Executing direct command: {query}")
            task_result = self.task_executor.execute_task(query)
            
            # Speak the response
            self.tts.speak(task_result)
            
            return task_result
        else:
            # Use NLP to understand the query
            try:
                # For non-direct commands, use NLP processing
                nlp_result = self.nlp_processor.process_query(query)
                
                # Generate a natural language response
                response = self.nlp_processor.generate_response(nlp_result)
                
                # Speak the response
                self.tts.speak(response)
                
                return response
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.tts.speak(error_msg)
                return error_msg