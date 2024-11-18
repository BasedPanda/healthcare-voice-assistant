import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional, Dict
import json
import os
from datetime import datetime
import threading
import queue

class SpeechHandler:
    def __init__(self, config: Dict = None):
        """
        Initialize speech recognition and synthesis components
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load default config
        self.config = {
            'speech_rate': 150,
            'speech_volume': 0.9,
            'voice_gender': 'female',  # 'male' or 'female'
            'timeout': 5,  # seconds to wait for speech
            'phrase_timeout': 3,  # seconds to wait for phrase completion
            'energy_threshold': 4000,  # minimum audio energy to detect
            'dynamic_energy_threshold': True,
            'wake_words': ['assistant', 'hey assistant', 'hello assistant']
        }
        
        # Update with provided config
        if config:
            self.config.update(config)

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.config['energy_threshold']
        self.recognizer.dynamic_energy_threshold = self.config['dynamic_energy_threshold']
        
        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            self.logger.error(f"Error initializing microphone: {e}")
            raise
            
        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config['speech_rate'])
            self.engine.setProperty('volume', self.config['speech_volume'])
            
            # Set voice gender
            voices = self.engine.getProperty('voices')
            if voices:
                desired_voice = [v for v in voices if self.config['voice_gender'] in v.name.lower()]
                if desired_voice:
                    self.engine.setProperty('voice', desired_voice[0].id)
                    
        except Exception as e:
            self.logger.error(f"Error initializing text-to-speech: {e}")
            raise
            
        # Initialize audio feedback sounds
        self.listening_sound_played = False
        
        # Speech queue for background TTS
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()

    def listen(self, play_sound: bool = True) -> Optional[str]:
        """
        Listen for voice input and convert to text
        
        Args:
            play_sound: Whether to play audio feedback when starting to listen
            
        Returns:
            str: Recognized text, or None if recognition failed
        """
        try:
            with self.microphone as source:
                if play_sound and not self.listening_sound_played:
                    self._play_listening_sound()
                    self.listening_sound_played = True
                
                self.logger.info("Listening...")
                
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.config['timeout'],
                        phrase_time_limit=self.config['phrase_timeout']
                    )
                    
                    # Reset listening sound flag
                    self.listening_sound_played = False
                    
                    # Convert speech to text
                    text = self.recognizer.recognize_google(audio)
                    self.logger.info(f"Recognized: {text}")
                    
                    # Check for wake word if configured
                    if self.config['wake_words']:
                        text_lower = text.lower()
                        if not any(wake_word in text_lower for wake_word in self.config['wake_words']):
                            return None
                        
                        # Remove wake word from text
                        for wake_word in self.config['wake_words']:
                            text_lower = text_lower.replace(wake_word, '').strip()
                        text = text_lower
                    
                    return text
                    
                except sr.WaitTimeoutError:
                    self.logger.info("Listening timeout - no speech detected")
                    self.listening_sound_played = False
                    return None
                    
                except sr.UnknownValueError:
                    self.logger.info("Speech not understood")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return None

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            wait: Whether to wait for speech to complete
        """
        if wait:
            self._speak_sync(text)
        else:
            self.speech_queue.put(text)

    def _speak_sync(self, text: str) -> None:
        """Synchronous text-to-speech conversion"""
        try:
            self.logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")

    def _process_speech_queue(self) -> None:
        """Process queued speech in background thread"""
        while True:
            try:
                text = self.speech_queue.get()
                self._speak_sync(text)
                self.speech_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing speech queue: {e}")

    def _play_listening_sound(self) -> None:
        """Play a sound to indicate the system is listening"""
        try:
            # You could implement actual sound playing here
            # For now, we'll just use a short beep via TTS
            self.engine.say("beep")
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error playing listening sound: {e}")

    def adjust_for_ambient_noise(self, duration: int = 1) -> None:
        """
        Adjust the recognizer's energy threshold for ambient noise
        
        Args:
            duration: Number of seconds to sample ambient noise
        """
        try:
            with self.microphone as source:
                self.logger.info(f"Adjusting for ambient noise - duration: {duration}s")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                
        except Exception as e:
            self.logger.error(f"Error adjusting for ambient noise: {e}")

    def save_audio(self, audio_data: sr.AudioData, filename: str = None) -> str:
        """
        Save audio data to a file
        
        Args:
            audio_data: AudioData object to save
            filename: Optional filename, defaults to timestamp
            
        Returns:
            str: Path to saved audio file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"
                
            # Create audio directory if it doesn't exist
            os.makedirs('audio', exist_ok=True)
            filepath = os.path.join('audio', filename)
            
            # Save audio file
            with open(filepath, "wb") as f:
                f.write(audio_data.get_wav_data())
                
            self.logger.info(f"Audio saved to: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            return ""

    def set_speech_rate(self, rate: int) -> None:
        """
        Set the speech rate
        
        Args:
            rate: Words per minute
        """
        try:
            self.config['speech_rate'] = rate
            self.engine.setProperty('rate', rate)
        except Exception as e:
            self.logger.error(f"Error setting speech rate: {e}")

    def set_speech_volume(self, volume: float) -> None:
        """
        Set the speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            self.config['speech_volume'] = volume
            self.engine.setProperty('volume', volume)
        except Exception as e:
            self.logger.error(f"Error setting speech volume: {e}")

    def stop_speaking(self) -> None:
        """Stop current speech output"""
        try:
            self.engine.stop()
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")