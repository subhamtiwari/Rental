# AI Leasing Agent Voice Bot

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/flask-2.x-lightgrey)](https://flask.palletsprojects.com/) [![Twilio](https://img.shields.io/badge/twilio-sdk-red)](https://www.twilio.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A conversational AI-powered voice assistant for apartment leasing offices, capable of handling incoming calls, understanding tenant inquiries, and providing real-time property information.

Built with [Cursor AI](https://cursor.sh/) and powered by Groq's Llama 3 model.

---

## 🚀 Features

- **Answer Incoming Calls**: Automatically answers and manages phone calls via Twilio Programmable Voice.
- **Speech Recognition**: Transcribes caller audio using Twilio `<Gather>` (STT).
- **Natural Language Understanding**: Routes caller queries to a Large Language Model (`llama3-8b-8192`) via the Groq API to interpret intent.
- **Property Data Retrieval**: Fetches apartment details (price, availability, amenities, hours, pet policy) from a simulated database.
- **Text-to-Speech Responses**: Converts LLM-generated replies to speech using Twilio TTS.
- **Multi-Turn Conversations**: Maintains conversational context and prompts follow-ups (e.g., "Anything else I can help you with?").
- **Error Handling**: Gracefully handles API timeouts, STT/TTS failures, and unexpected inputs.


## 🏗️ Tech Stack

| Component                  | Technology                          |
|----------------------------|-------------------------------------|
| **Backend**                | Python 3.x, Flask                   |
| **Telephony & STT/TTS**    | Twilio Programmable Voice           |
| **LLM**                    | Groq API (`llama3-8b-8192`)         |
| **Environment Management** | `python-dotenv`                     |
| **Tunnel for Local Testing** | `ngrok`                            |


## 📐 Architecture Overview

1. **Twilio Webhook**: Incoming call triggers `/voice` endpoint.
2. **Audio Capture**: `<Gather>` records caller speech and sends transcript.
3. **LLM Query**: Transcript forwarded to Groq Llama 3 via OpenAI-compatible API.
4. **Data Lookup**: LLM decides if DB query is needed; fetches from in-memory store.
5. **TTS Response**: LLM output converted to audio by Twilio and returned to caller.

*Diagram placeholder: `docs/architecture.png`*


## ⚙️ Getting Started

### Prerequisites
- Python 3.8+
- [Twilio account & phone number](https://www.twilio.com/console)
- [Ngrok account for tunneling](https://ngrok.com/)
- Groq API key


### Installation

```bash
# Clone the repository
git clone <YOUR_REPO_URL>
cd <REPO_NAME>

# Create & activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```


### Configuration

1. Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2. Set your credentials in `.env`:
    ```dotenv
    GROQ_API_KEY="gsk_YourActualGroqApiKey"
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    TWILIO_AUTH_TOKEN="your_auth_token"
    ```
3. Exclude `.env` from version control:
    ```bash
    echo ".env" >> .gitignore
    ```


## ▶️ Running Locally

1. **Start Flask server**:
    ```bash
    flask run --port 8080
    ```

2. **Expose via ngrok**:
    ```bash
    ngrok http 8080
    ```
    Copy the generated HTTPS URL.

3. **Configure Twilio Webhook**:
    - In Twilio Console → Phone Numbers → Manage → Active Numbers.
    - For your number, set **Voice & Fax** → **A CALL COMES IN** to Webhook POST: `{NGROK_URL}/voice`

4. **Test Call**:
    Dial your Twilio number and interact with the bot. Check Flask logs for debugging.


## 🔮 Future Enhancements

- Integrate a real database (PostgreSQL, Supabase).
- Advanced state management & memory for rich dialogues.
- Function calls: schedule tours, submit applications, etc.
- Enhanced STT/TTS: OpenAI Whisper, ElevenLabs.
- Dockerize & helm charts for Kubernetes deploy.
- Comprehensive unit & integration tests.


## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Commit your changes (`git commit -m 'Add xyz feature'`)
4. Push to branch (`git push origin feature/xyz`)
5. Open a Pull Request

For major changes, discuss via issue first.


## 📄 License

This project is licensed under the [MIT License](LICENSE).

