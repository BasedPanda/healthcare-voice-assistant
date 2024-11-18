# Healthcare Voice Assistant

A voice-enabled assistant for scheduling healthcare appointments using speech recognition and natural language processing.

## Features

- Voice command recognition for appointment scheduling
- Natural language processing for intent understanding
- Text-to-speech responses
- Appointment management (schedule, check, cancel)
- Persistent storage of appointments

## Setup

1. Clone the repository:
```bash
git clone 
cd healthcare_voice_assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy .env.example to .env and configure as needed:
```bash
cp .env.example .env
```

5. Run the application:
```bash
python app.py
```

## Usage

Speak commands like:
- "Schedule an appointment for tomorrow at 2 PM"
- "Check my appointments"
- "Cancel my appointment for Friday"
- "Exit" to close the application
