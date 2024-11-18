import spacy
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import re
from dateutil import parser
import logging

class IntentProcessor:
    def __init__(self):
        """Initialize the NLP processor with spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model isn't downloaded, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            
        # Define intent patterns
        self.intent_patterns = {
            'SCHEDULE_APPOINTMENT': [
                r'schedule',
                r'book',
                r'make',
                r'set up',
                r'arrange'
            ],
            'CHECK_APPOINTMENTS': [
                r'check',
                r'view',
                r'show',
                r'list',
                r'what are',
                r'do i have'
            ],
            'CANCEL_APPOINTMENT': [
                r'cancel',
                r'delete',
                r'remove',
                r'reschedule'
            ],
            'EXIT': [
                r'exit',
                r'quit',
                r'goodbye',
                r'bye'
            ]
        }
        
        # Define doctor specialties
        self.doctor_specialties = {
            'general': ['doctor', 'physician', 'gp', 'general practitioner'],
            'cardiology': ['cardiologist', 'heart doctor', 'heart specialist'],
            'dermatology': ['dermatologist', 'skin doctor', 'skin specialist'],
            'pediatrics': ['pediatrician', 'children doctor', 'child specialist'],
            'neurology': ['neurologist', 'brain doctor', 'nerve specialist']
        }

    def process(self, text: str) -> Tuple[str, Dict]:
        """
        Process text input and determine intent and entities
        
        Args:
            text: Input text from speech recognition
            
        Returns:
            Tuple of (intent_name, entities_dict)
        """
        text = text.lower().strip()
        doc = self.nlp(text)
        
        # Detect intent
        intent = self._detect_intent(text)
        
        # Extract entities based on intent
        entities = {}
        if intent == "SCHEDULE_APPOINTMENT" or intent == "CANCEL_APPOINTMENT":
            entities = self._extract_appointment_entities(doc, text)
            
        return intent, entities

    def _detect_intent(self, text: str) -> str:
        """Detect the intent from the input text"""
        for intent, patterns in self.intent_patterns.items():
            if any(re.search(rf'\b{pattern}\b', text) for pattern in patterns):
                return intent
        return "UNKNOWN"

    def _extract_appointment_entities(self, doc, text: str) -> Dict:
        """
        Extract entities (date, time, doctor) from the text
        
        Returns dictionary with extracted entities
        """
        entities = {
            'date': None,
            'time': None,
            'doctor': None
        }
        
        # Extract date and time
        date_time = self._extract_datetime(text)
        if date_time:
            entities['date'] = date_time.get('date')
            entities['time'] = date_time.get('time')
            
        # Extract doctor/specialty
        doctor = self._extract_doctor(text)
        if doctor:
            entities['doctor'] = doctor
            
        return entities

    def _extract_datetime(self, text: str) -> Optional[Dict]:
        """Extract date and time from text"""
        try:
            # Common time patterns
            time_patterns = [
                r'(\d{1,2}):(\d{2})',                    # 14:30, 2:30
                r'(\d{1,2})\s*(am|pm)',                  # 2 pm, 11am
                r'(\d{1,2}):(\d{2})\s*(am|pm)',         # 2:30 pm, 11:30am
                r'(\d{1,2})\s*o[\'']?clock'             # 2 o'clock
            ]
            
            # Try to extract time first
            time_str = None
            for pattern in time_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    time_str = match.group(0)
                    break
            
            # Parse the complete text for date
            parsed_date = parser.parse(text, fuzzy=True)
            
            # If we found a specific time, use it; otherwise use parsed_date's time
            if time_str:
                try:
                    parsed_time = parser.parse(time_str).time()
                except:
                    parsed_time = parsed_date.time()
            else:
                parsed_time = parsed_date.time()
            
            # Handle relative dates (tomorrow, next week, etc.)
            if 'tomorrow' in text:
                parsed_date = datetime.now() + timedelta(days=1)
            elif 'next week' in text:
                parsed_date = datetime.now() + timedelta(weeks=1)
            
            return {
                'date': parsed_date.strftime('%Y-%m-%d'),
                'time': parsed_time.strftime('%H:%M')
            }
            
        except (ValueError, TypeError):
            return None

    def _extract_doctor(self, text: str) -> Optional[str]:
        """Extract doctor specialty from text"""
        text = text.lower()
        
        # Check for specific doctor mentions
        doctor_match = re.search(r'dr\.?\s+(\w+)', text)
        if doctor_match:
            return f"Dr. {doctor_match.group(1).capitalize()}"
            
        # Check for specialties
        for specialty, keywords in self.doctor_specialties.items():
            if any(keyword in text for keyword in keywords):
                # Format specialty name
                specialty_name = specialty.capitalize()
                return f"Dr. {specialty_name} (Specialist)"
                
        # Default to general physician if no specific doctor/specialty found
        return "Dr. General (General Physician)"

    def get_confirmation(self, text: str) -> bool:
        """
        Determine if the text is a confirmation (yes/no)
        
        Args:
            text: Input text
            
        Returns:
            bool: True for confirmation, False for denial
        """
        text = text.lower().strip()
        
        confirmations = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'confirm']
        denials = ['no', 'nope', 'nah', 'cancel', 'don\'t']
        
        return any(word in text for word in confirmations) and not any(word in text for word in denials)

    def format_appointment_summary(self, entities: Dict) -> str:
        """
        Format appointment details for confirmation
        
        Args:
            entities: Dictionary of extracted entities
            
        Returns:
            str: Formatted appointment summary
        """
        if not entities.get('date') or not entities.get('time'):
            return "I couldn't understand the appointment time details."
            
        try:
            date_obj = datetime.strptime(entities['date'], '%Y-%m-%d')
            time_obj = datetime.strptime(entities['time'], '%H:%M')
            
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
            formatted_time = time_obj.strftime('%I:%M %p')
            
            doctor = entities.get('doctor', 'General Physician')
            
            return f"Appointment with {doctor} on {formatted_date} at {formatted_time}"
            
        except ValueError:
            return "There was an error formatting the appointment details."