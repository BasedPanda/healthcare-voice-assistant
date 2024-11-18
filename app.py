import logging
import sys
import os
from datetime import datetime
from typing import Optional, Tuple, Dict
import json
from pathlib import Path

# Import our components
from .speech.speech_handler import SpeechHandler
from .nlp.intent_processor import IntentProcessor
from .scheduling.appointment import AppointmentManager
from .database.db_manager import DatabaseManager

class HealthcareVoiceAssistant:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the healthcare voice assistant
        
        Args:
            config_path: Optional path to configuration file
        """
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        try:
            self.speech = SpeechHandler(self.config.get('speech', {}))
            self.nlp = IntentProcessor()
            self.scheduler = AppointmentManager()
            self.db = DatabaseManager()
            
            self.logger.info("Healthcare Voice Assistant initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def _setup_logging(self):
        """Configure logging for the application"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(
            f"logs/healthcare_assistant_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'speech': {
                'speech_rate': 150,
                'speech_volume': 0.9,
                'voice_gender': 'female',
                'timeout': 5,
                'wake_words': ['assistant', 'hey assistant', 'hello assistant']
            },
            'scheduling': {
                'working_hours_start': 9,
                'working_hours_end': 17,
                'appointment_duration': 30
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        return default_config

    def start(self):
        """Start the voice assistant"""
        self.speech.speak("Healthcare Voice Assistant is ready. How can I help you today?")
        
        while True:
            try:
                # Listen for voice input
                voice_input = self.speech.listen()
                if not voice_input:
                    continue
                    
                # Process the intent
                intent, entities = self.nlp.process(voice_input)
                
                # Handle the intent
                self._handle_intent(intent, entities)
                
            except KeyboardInterrupt:
                self.speech.speak("Goodbye!")
                self.logger.info("Assistant terminated by user")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.speech.speak("I encountered an error. Please try again.")

    def _handle_intent(self, intent: str, entities: Dict):
        """Handle different intents based on NLP processing"""
        try:
            if intent == "SCHEDULE_APPOINTMENT":
                self._handle_scheduling(entities)
            elif intent == "CHECK_APPOINTMENTS":
                self._handle_checking_appointments()
            elif intent == "CANCEL_APPOINTMENT":
                self._handle_cancellation(entities)
            elif intent == "EXIT":
                self.speech.speak("Goodbye!")
                sys.exit(0)
            else:
                self._handle_unknown_intent()
                
        except Exception as e:
            self.logger.error(f"Error handling intent {intent}: {e}")
            self.speech.speak("I'm sorry, I couldn't process that request. Please try again.")

    def _handle_scheduling(self, entities: Dict):
        """Handle appointment scheduling intent"""
        try:
            # Check if we have all required information
            if not entities.get('date') or not entities.get('time'):
                self.speech.speak("I need both a date and time for the appointment. When would you like to schedule it?")
                return
                
            # Verify availability
            if not self.scheduler.is_available(entities['date'], entities['time']):
                alternative_slots = self.scheduler.suggest_alternative_slots(
                    entities['date'],
                    entities['time'],
                    num_suggestions=3
                )
                
                if alternative_slots:
                    self.speech.speak(
                        "That time is not available. Here are some alternative slots: "
                        + self._format_alternative_slots(alternative_slots)
                    )
                    return
                else:
                    self.speech.speak("I'm sorry, there are no available slots around that time.")
                    return
                    
            # Schedule the appointment
            success, message = self.scheduler.schedule_appointment(
                date=entities['date'],
                time=entities['time'],
                doctor=entities.get('doctor', 'General Physician'),
                notes=entities.get('notes', '')
            )
            
            if success:
                self.speech.speak(f"Great! {message}")
            else:
                self.speech.speak(f"I'm sorry, I couldn't schedule the appointment. {message}")
                
        except Exception as e:
            self.logger.error(f"Error in appointment scheduling: {e}")
            self.speech.speak("There was an error scheduling your appointment. Please try again.")

    def _handle_checking_appointments(self):
        """Handle checking appointments intent"""
        try:
            appointments = self.scheduler.get_appointments()
            
            if not appointments:
                self.speech.speak("You have no upcoming appointments scheduled.")
                return
                
            response = "Here are your upcoming appointments: "
            for apt in appointments[:3]:  # Limit to 3 appointments for voice
                response += f"On {self._format_date(apt['date'])} at {self._format_time(apt['time'])} "
                response += f"with {apt['doctor']}. "
                
            if len(appointments) > 3:
                response += f"And {len(appointments) - 3} more appointments."
                
            self.speech.speak(response)
            
        except Exception as e:
            self.logger.error(f"Error checking appointments: {e}")
            self.speech.speak("I had trouble retrieving your appointments. Please try again.")

    def _handle_cancellation(self, entities: Dict):
        """Handle appointment cancellation intent"""
        try:
            if not entities.get('date') or not entities.get('time'):
                self.speech.speak("I need both the date and time of the appointment you want to cancel.")
                return
                
            success, message = self.scheduler.cancel_appointment(
                entities['date'],
                entities['time']
            )
            
            if success:
                self.speech.speak("The appointment has been cancelled successfully.")
            else:
                self.speech.speak(f"I couldn't cancel the appointment. {message}")
                
        except Exception as e:
            self.logger.error(f"Error in appointment cancellation: {e}")
            self.speech.speak("There was an error cancelling your appointment. Please try again.")

    def _handle_unknown_intent(self):
        """Handle unknown or unclear intents"""
        self.speech.speak(
            "I'm not sure what you'd like to do. You can schedule an appointment, "
            "check your appointments, or cancel an appointment. What would you like to do?"
        )

    def _format_alternative_slots(self, slots: list) -> str:
        """Format alternative time slots for speech output"""
        formatted = ""
        for slot in slots:
            formatted += f"{self._format_date(slot['date'])} at {self._format_time(slot['time'])}, "
        return formatted.rstrip(', ')

    def _format_date(self, date_str: str) -> str:
        """Format date for speech output"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%A, %B %d')

    def _format_time(self, time_str: str) -> str:
        """Format time for speech output"""
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%I:%M %p')

def main():
    """Main entry point for the application"""
    try:
        # Get config path from environment or use default
        config_path = os.getenv('HEALTHCARE_ASSISTANT_CONFIG')
        
        # Create and start the assistant
        assistant = HealthcareVoiceAssistant(config_path)
        assistant.start()
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()