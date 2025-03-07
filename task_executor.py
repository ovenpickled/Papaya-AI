import os
import subprocess
import datetime
import time
import threading
import win32com.client
import win32api
import win32con
import win32gui
import win32process
import re

class TaskExecutor:
    def __init__(self):
        self.shell = win32com.client.Dispatch("WScript.Shell")
    
    def execute_task(self, task_description):
        """Execute a task based on the description"""
        task_description = task_description.lower()
        print(f"Task executor processing: {task_description}")
        
        # Open application
        if "open" in task_description:
            app_match = re.search(r"open\s+(.*?)(?:\s+|$)", task_description)
            if app_match:
                app_name = app_match.group(1).strip()
                return self.open_application(app_name)
        
        # Switch between applications - improved pattern matching
        elif "switch" in task_description:
            print("Switch command detected")
            if "next" in task_description or "between" in task_description:
                return self.switch_to_next_app()
            
            # Improved regex to better capture app names
            app_match = re.search(r"switch\s+(?:to\s+)?(.*?)(?:\s+|$)", task_description)
            if app_match:
                app_name = app_match.group(1).strip()
                print(f"Extracted app name: {app_name}")
                return self.switch_to_app(app_name)
        
        # Set alarm
        elif "set alarm" in task_description or "set a alarm" in task_description or "set an alarm" in task_description:
            time_match = re.search(r"(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?", task_description)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                
                # Fix AM/PM detection
                if period and period.lower() == "pm" and hour < 12:
                    hour += 12
                elif period and period.lower() == "am" and hour == 12:
                    hour = 0
                
                # Check for "p.m." or "a.m." format
                if "p.m." in task_description and hour < 12:
                    hour += 12
                elif "a.m." in task_description and hour == 12:
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
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "edge": "msedge.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "explorer": "explorer.exe",
            "settings": "explorer.exe ms-settings:",
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
    
    def switch_to_next_app(self):
        """Switch to the next application using Alt+Tab"""
        try:
            print("Attempting to switch to next app using Alt+Tab")
            # Simulate pressing Alt+Tab
            self.shell.SendKeys("%{TAB}")
            return "Switched to the next application"
        except Exception as e:
            print(f"Error switching to next app: {e}")
            return f"Failed to switch applications: {str(e)}"

    def switch_to_app(self, app_name):
        """Switch to a specific application by name using win32gui"""
        try:
            print(f"Attempting to switch to: {app_name}")
            
            # Try to find the application in our dictionary
            app_paths = {
                "notepad": "Notepad",
                "calculator": "Calculator",
                "word": "Word",
                "excel": "Excel",
                "chrome": "Chrome",
                "brave": "Brave",
                "edge": "Edge",
                "firefox": "Firefox",
                "explorer": "Explorer",
                "settings": "Settings",
            }
            
            # Find the window title to activate
            window_title = None
            for key, title in app_paths.items():
                if key in app_name.lower():
                    window_title = title
                    print(f"Found matching title: {window_title}")
                    break
            
            # If not found in our dictionary, use the app_name directly
            if not window_title:
                window_title = app_name
                print(f"Using direct title: {window_title}")
            
            # Use win32gui to find and activate the window
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text and window_title.lower() in window_text.lower():
                        results.append((hwnd, window_text))
            
            results = []
            win32gui.EnumWindows(enum_windows_callback, results)
            print(f"Found {len(results)} potential matching windows")
            
            if results:
                # Activate the first matching window
                hwnd, matched_title = results[0]
                try:
                    # Ensure the window is not minimized
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    
                    # Set as foreground window
                    current_thread = win32api.GetCurrentThreadId()
                    window_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                    
                    if current_thread != window_thread:
                        win32process.AttachThreadInput(current_thread, window_thread, True)
                        win32gui.SetForegroundWindow(hwnd)
                        win32process.AttachThreadInput(current_thread, window_thread, False)
                    else:
                        win32gui.SetForegroundWindow(hwnd)
                    
                    return f"Switched to {matched_title}"
                except Exception as e:
                    print(f"Error activating window: {e}")
                    # Try the AppActivate as a fallback
                    try:
                        self.shell.AppActivate(matched_title)
                        return f"Switched to {matched_title}"
                    except:
                        pass
            
            # If we get here, try one more approach - partial matching with Shell.AppActivate
            try:
                # Try with just the first word of the app name
                first_word = window_title.split()[0]
                result = self.shell.AppActivate(first_word)
                if result:
                    return f"Switched to application containing '{first_word}'"
            except:
                pass
                
            return f"Could not find {window_title}. Make sure the application is running."
        except Exception as e:
            print(f"Error in switch_to_app: {e}")
            # Don't return the error message to the user
            return f"I couldn't switch to {app_name}. Please make sure it's running."
    
    def set_alarm(self, hour, minute):
        """Set an alarm using a custom alarm UI"""
        now = datetime.datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has already passed today, set it for tomorrow
        if alarm_time < now:
            alarm_time += datetime.timedelta(days=1)
        
        time_diff = alarm_time - now
        seconds = time_diff.total_seconds()
        
        # Format the time for display
        formatted_time = alarm_time.strftime("%I:%M %p")
        
        # Create a simple UI to show the alarm is set
        try:
            # Use win32api.MessageBox instead of shell.Popup
            win32api.MessageBox(
                0,  # Handle to owner window
                f"Alarm set for {formatted_time}\nClick OK to dismiss this notification.",
                "Alarm Set",
                win32con.MB_OK | win32con.MB_ICONINFORMATION
            )
        except Exception as e:
            print(f"Failed to create alarm UI: {e}")
        
        # Create a thread to wait for the alarm time
        def alarm_thread():
            print(f"Alarm set for {hour:02d}:{minute:02d} ({formatted_time})")
            time.sleep(seconds)
            
            # Play sound when alarm time is reached
            try:
                import winsound
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                for _ in range(5):
                    winsound.Beep(1000, 1000)
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error playing sound: {e}")
                
            # Show alarm notification using win32api.MessageBox
            try:
                win32api.MessageBox(
                    0,
                    f"ALARM: {formatted_time}",
                    "Your Alarm",
                    win32con.MB_OK | win32con.MB_ICONEXCLAMATION
                )
            except Exception as e:
                print(f"Failed to show alarm notification: {e}")
        
        alarm_thread = threading.Thread(target=alarm_thread)
        alarm_thread.daemon = True
        alarm_thread.start()
        
        return f"Alarm set for {formatted_time}. The alarm will sound at that time."
    
    def check_weather(self, location):
        """Check weather for a location by opening a weather website"""
        try:
            url = f"https://www.weather.com/weather/today/l/{location.replace(' ', '+')}"
            subprocess.Popen(["explorer", url])
            return f"Checking weather for {location}"
        except Exception as e:
            return f"Failed to check weather: {str(e)}"