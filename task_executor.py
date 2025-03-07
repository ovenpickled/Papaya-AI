import os
import subprocess
import datetime
import win32com.client
import re

class TaskExecutor:
    def __init__(self):
        self.shell = win32com.client.Dispatch("WScript.Shell")
    
    def execute_task(self, task_description):
        """Execute a task based on the description"""
        task_description = task_description.lower()
        
        # Open application
        if "open" in task_description:
            app_match = re.search(r"open\s+(.*?)(?:\s+|$)", task_description)
            if app_match:
                app_name = app_match.group(1).strip()
                return self.open_application(app_name)
        
        # Set alarm
        elif "set alarm" in task_description or "set a alarm" in task_description or "set an alarm" in task_description:
            time_match = re.search(r"(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?", task_description)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                
                if period == "pm" and hour < 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                return self.set_alarm(hour, minute)
        
        # Check weather
        elif "weather" in task_description:
            location_match = re.search(r"weather\s+(?:in|for|at)\s+(.*?)(?:\s+|$)", task_description)
            location = location_match.group(1) if location_match else "current location"
            return self.check_weather(location)
            
        return f"I'm not sure how to perform this task: {task_description}"
    
    def open_application(self, app_name):
        """Open an application by name"""
        app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": "msedge.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "explorer": "explorer.exe",
            "settings": "ms-settings:",
        }
        
        # Try to find the application in our dictionary
        for key, path in app_paths.items():
            if key in app_name:
                try:
                    subprocess.Popen(path)
                    return f"Opening {key}"
                except Exception as e:
                    return f"Failed to open {key}: {str(e)}"
        
        # If not found, try to run it directly
        try:
            self.shell.Run(app_name)
            return f"Attempting to open {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    
    def set_alarm(self, hour, minute):
        """Set an alarm using Windows built-in alarm app"""
        now = datetime.datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has already passed today, set it for tomorrow
        if alarm_time < now:
            alarm_time += datetime.timedelta(days=1)
        
        time_diff = alarm_time - now
        seconds = time_diff.total_seconds()
        
        # Open the alarm app
        try:
            subprocess.Popen("explorer.exe ms-clock:")
            return f"Setting alarm for {hour:02d}:{minute:02d}"
        except Exception as e:
            return f"Failed to open alarm app: {str(e)}"
    
    def check_weather(self, location):
        """Check weather for a location by opening a weather website"""
        try:
            url = f"https://www.weather.com/weather/today/l/{location.replace(' ', '+')}"
            subprocess.Popen(["explorer", url])
            return f"Checking weather for {location}"
        except Exception as e:
            return f"Failed to check weather: {str(e)}"