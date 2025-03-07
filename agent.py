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
        # Check for approval or rejection commands first
        lower_query = query.lower()
    
        if lower_query.startswith("approve ") or lower_query == "approve":
            try:
                # Extract task ID if present
                parts = lower_query.split()
                task_id = int(parts[1]) if len(parts) > 1 else 1
                task_result = self.task_executor.approve_task(task_id)
                self.tts.speak(task_result)
                return task_result
            except (IndexError, ValueError):
                response = "Please specify a valid task ID to approve."
                self.tts.speak(response)
                return response
    
        if lower_query.startswith("reject ") or lower_query == "reject":
            try:
            # Extract task ID if present
                parts = lower_query.split()
                task_id = int(parts[1]) if len(parts) > 1 else 1
                task_result = self.task_executor.reject_task(task_id)
                self.tts.speak(task_result)
                return task_result
            except (IndexError, ValueError):
                response = "Please specify a valid task ID to reject."
                self.tts.speak(response)
                return response
    
    # Rest of your existing code for direct commands and NLP processing
    # Direct command patterns
        direct_commands = [
        "open", "switch", "set alarm", "set a alarm", "set an alarm", 
        "weather", "check weather", "forecast", "send money", "transfer", 
        "pay", "payment", "transaction", "balance", "transactions", "history"
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
        # Your existing NLP processing code

    
            # Use NLP to understand the query
            try:
                # For non-direct commands, use NLP processing
                nlp_result = self.nlp_processor.process_query(query)
                print(f"NLP result: {nlp_result}")
                
                # Check if the result looks like JSON
                if nlp_result and (nlp_result.startswith('{') or nlp_result.startswith('[')):
                    try:
                        # Try to parse it as JSON
                        parsed_result = json.loads(nlp_result)
                        
                        # If it has intent and entities, try to execute the task
                        if 'intent' in parsed_result:
                            intent = parsed_result.get('intent')
                            
                            # Handle weather intent
                            if intent == 'check_weather' and 'entities' in parsed_result:
                                location = parsed_result['entities'].get('location', 'current location')
                                task_result = self.task_executor.check_weather(location)
                                self.tts.speak(task_result)
                                return task_result
                    except json.JSONDecodeError:
                        print("Failed to parse NLP result as JSON")
                
                    # Generate a natural language response
                response = self.nlp_processor.generate_response(nlp_result)
                
                    # Speak the response
                self.tts.speak(response)
                
                return response
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.tts.speak(error_msg)
                return error_msg