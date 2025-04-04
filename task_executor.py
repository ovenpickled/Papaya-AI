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
import requests
from dotenv import load_dotenv
from payment_service import StripePaymentService
import re

# Load environment variables
load_dotenv()

class TaskExecutor:
    def __init__(self):
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.payment_service = StripePaymentService()
    
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
        
        # Check weather - improved pattern matching
        elif "weather" in task_description or "forecast" in task_description:
            location_match = re.search(r"(?:weather|forecast)\s+(?:in|for|at|of)\s+(.*?)(?:\s+|$)", task_description)
            if location_match:
                location = location_match.group(1).strip()
            else:
                # Try to find any location mentioned in the query
                location_match = re.search(r"(?:weather|forecast).*?([\w\s]+)$", task_description)
                if location_match:
                    location = location_match.group(1).strip()
                else:
                    location = "current location"
            
            return self.check_weather(location)
            
        # return f"I'm not sure how to perform this task: {task_description}"
    
        # Add payment processing
        elif any(keyword in task_description for keyword in ["pay", "payment", "charge", "send money"]):
        
            return self.process_payment(task_description)
        
        # Check payment status
        elif "payment status" in task_description or "check payment" in task_description:
            return self.check_payment_status(task_description)
                
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
        """Check weather for a location using Open-Meteo API"""
        try:
            # Handle "current location" by using a default city
            if location.lower() == "current location":
                location = "New York"  # Default location
                
            print(f"Checking weather for: {location}")
            
            # First, we need to geocode the location to get coordinates
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geo_response = requests.get(geocoding_url)
            
            if geo_response.status_code != 200 or not geo_response.json().get("results"):
                return f"I couldn't find the location '{location}'. Please check the spelling or try a different location."
            
            # Extract coordinates
            geo_data = geo_response.json()["results"][0]
            latitude = geo_data["latitude"]
            longitude = geo_data["longitude"]
            city_name = geo_data["name"]
            country = geo_data.get("country", "")
            
            print(f"Found location: {city_name}, {country} at {latitude}, {longitude}")
            
            # Get weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&timezone=auto"
            weather_response = requests.get(weather_url)
            
            if weather_response.status_code == 200:
                data = weather_response.json()
                current = data["current"]
                
                # Map weather code to description
                weather_codes = {
                    0: "Clear sky",
                    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Fog", 48: "Depositing rime fog",
                    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                    77: "Snow grains",
                    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                    85: "Slight snow showers", 86: "Heavy snow showers",
                    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
                }
                
                weather_description = weather_codes.get(current["weather_code"], "Unknown")
                
                # Format the weather information
                weather_info = (
                    f"Current weather in {city_name}, {country}:\n"
                    f"• Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)\n"
                    f"• Condition: {weather_description}\n"
                    f"• Humidity: {current['relative_humidity_2m']}%\n"
                    f"• Wind speed: {current['wind_speed_10m']} km/h\n"
                    f"• Precipitation: {current['precipitation']} mm"
                )
                
                print(f"Weather data: {weather_info}")
                
                # Display the weather information in a message box
                win32api.MessageBox(
                    0,
                    weather_info,
                    f"Weather for {city_name}",
                    win32con.MB_OK | win32con.MB_ICONINFORMATION
                )
                
                return f"The current weather in {city_name} is {current['temperature_2m']}°C with {weather_description.lower()}."
            else:
                print(f"Error from weather API: {weather_response.status_code}")
                return f"Sorry, I couldn't get the weather data. Please try again later."
        except Exception as e:
            print(f"Error checking weather: {e}")
            return f"I encountered an error while checking the weather for {location}."
        
    def process_payment(self, task_description):
        """Process a payment based on voice command"""
        # Extract amount
        amount_match = re.search(r"(\$?\d+(?:\.\d{1,2})?)", task_description)
        if not amount_match:
            return "I couldn't determine the payment amount. Please specify an amount like $10 or 25 dollars."
        
        amount_str = amount_match.group(1).replace("$", "")
        # Convert to cents for Stripe
        amount_cents = int(float(amount_str) * 100)
        
        # Extract description if available
        description_match = re.search(r"for\s+([\w\s]+)(?:$|\.)", task_description)
        description = description_match.group(1) if description_match else "Voice payment"
        
        # Create payment intent
        result = self.payment_service.create_payment_intent(
            amount=amount_cents,
            description=description
        )
        
        if result["success"]:
            payment_id = result["id"]
            client_secret = result["client_secret"]
            
            # In a real application, you would now:
            # 1. Store the payment_id for later reference
            # 2. Redirect to a payment form or display a QR code
            # 3. Use the client_secret with Stripe Elements or Checkout
            
            # For demo purposes, we'll just show a message box
            win32api.MessageBox(
                0,
                f"Payment of ${amount_str} initiated.\nPayment ID: {payment_id}\n\nIn a real app, this would open a payment form.",
                "Payment Initiated",
                win32con.MB_OK | win32con.MB_ICONINFORMATION
            )
            
            return f"I've initiated a payment for ${amount_str}. In a real application, you would now complete this payment through a secure form."
        else:
            win32api.MessageBox(
                0,
                f"Payment failed: {result['error']}",
                "Payment Failed",
                win32con.MB_OK | win32con.MB_ICONERROR
            )
            
            return f"Sorry, I couldn't process the payment: {result['error']}"

    def check_payment_status(self, task_description):
        """Check the status of a payment"""
        # Extract payment ID
        id_match = re.search(r"payment\s+(?:id\s+)?([a-zA-Z0-9_]+)", task_description)
        if not id_match:
            return "Please provide a payment ID to check its status."
        
        payment_id = id_match.group(1)
        result = self.payment_service.retrieve_payment_intent(payment_id)
        
        if result["success"]:
            status = result["status"]
            amount = result["amount"] / 100  # Convert cents to dollars
            
            win32api.MessageBox(
                0,
                f"Payment Status: {status}\nAmount: ${amount}",
                "Payment Status",
                win32con.MB_OK | win32con.MB_ICONINFORMATION
            )
            
            return f"The payment with ID {payment_id} has a status of {status}."
        else:
            win32api.MessageBox(
                0,
                f"Failed to retrieve payment status: {result['error']}",
                "Status Check Failed",
                win32con.MB_OK | win32con.MB_ICONERROR
            )
            
            return f"Sorry, I couldn't check the payment status: {result['error']}"