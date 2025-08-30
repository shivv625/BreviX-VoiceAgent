# Brevix - Advanced AI Voice Assistant

> **A sophisticated real-time voice assistant powered by cutting-edge AI technologies**

Brevix is an intelligent voice-powered conversational agent that combines speech recognition, natural language processing, and text-to-speech synthesis to create a seamless voice interaction experience. Built with modern web technologies and integrated with multiple AI services.

![Brevix Demo](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green) ![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange)

## ✨ Key Features

### 🎤 **Real-Time Speech Recognition**
- **Continuous Transcription**: Live speech-to-text using AssemblyAI's streaming API
- **High Accuracy**: Advanced speech recognition with noise suppression
- **Format Turns**: Intelligent sentence formatting and punctuation

### 🧠 **Intelligent Conversation**
- **Google Gemini Integration**: Powered by Gemini 1.5 Flash for natural conversations
- **Contextual Memory**: Maintains conversation history throughout the session
- **Personality**: Brevix has a unique persona as a futuristic AI robot

### 🔊 **Natural Text-to-Speech**
- **Murf AI Integration**: High-quality voice synthesis with natural intonation
- **Streaming Audio**: Real-time audio generation and playback
- **Voice Customization**: Uses Natalie voice with conversational style

### 🌐 **Smart Skills & Integrations**
- **Website Navigation**: Voice commands to open websites ("Open YouTube", "Go to Google")
- **Weather Information**: Real-time weather updates for any location
- **Web Search**: Intelligent search capabilities (integration ready)

### 🎨 **Modern Web Interface**
- **Glassmorphism Design**: Beautiful, modern UI with glass effects and gradients
- **Real-time Status**: Visual indicators for connection, listening, thinking, and speaking states
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Eye-friendly dark interface with cyan/orange accents

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │  External APIs  │
│   (Browser)     │    │   (FastAPI)      │    │                 │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Microphone  │ │◄──►│ │  WebSocket   │ │◄──►│ │ AssemblyAI  │ │
│ │ Audio Input │ │    │ │  Handler     │ │    │ │ (Speech)    │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │        │         │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Speaker     │ │◄──►│ │ LLM Response │ │◄──►│ │ Google      │ │
│ │ Audio Out   │ │    │ │ Generator    │ │    │ │ Gemini      │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │        │         │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Chat UI     │ │◄──►│ │ Special      │ │◄──►│ │ Murf AI     │ │
│ │ Display     │ │    │ │ Skills       │ │    │ │ (TTS)       │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **Microphone Access** (for voice input)
- **Internet Connection** (for AI services)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/brevix-voice-assistant.git
cd brevix-voice-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
MURF_API_KEY=your_murf_ai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Run the Application

```bash
python main.py
```

### 5. Access Brevix

Open your browser and navigate to:
```
http://localhost:8000
```

## 🔧 API Configuration

### Required API Keys

| Service | Purpose | How to Get |
|---------|---------|------------|
| **Google Gemini** | Language Model & Conversation | [Google AI Studio](https://makersuite.google.com/) |
| **AssemblyAI** | Speech Recognition | [AssemblyAI Console](https://www.assemblyai.com/) |
| **Murf AI** | Text-to-Speech | [Murf AI Platform](https://murf.ai/) |
| **Tavily** | Web Search (Optional) | [Tavily API](https://tavily.com/) |

### Configuration Options

1. **Environment Variables**: Set in `.env` file (recommended for development)
2. **Runtime Configuration**: Use the settings modal in the web interface
3. **Session-based**: API keys can be set per session without restarting

## 📁 Project Structure

```
brevix-voice-assistant/
├── 📄 main.py              # FastAPI application & WebSocket handlers
├── 📄 config.py            # Configuration and environment loading
├── 📄 requirements.txt     # Python dependencies
├── 📄 .env                 # Environment variables (create this)
├── 📄 .gitignore          # Git ignore patterns
├── 📁 static/             # Frontend static files
│   └── 📄 index.js        # Client-side JavaScript logic
├── 📁 templates/          # HTML templates
│   └── 📄 index.html      # Main web interface
└── 📄 README.md           # This file
```

## 🔄 How It Works

### 1. **Voice Input Processing**
```
Microphone → Browser Audio API → WebSocket → AssemblyAI → Transcript
```

### 2. **Intelligence Layer**
```
Transcript → Intent Detection → Special Skills OR Gemini AI → Response
```

### 3. **Voice Output Generation**
```
Text Response → Murf AI TTS → Audio Stream → Browser Audio → Speaker
```

### 4. **Special Skills Detection**
- **Website Opening**: Detects phrases like "open YouTube", "go to Google"
- **Weather Queries**: Processes "weather in [location]" requests
- **Future Skills**: Extensible architecture for adding new capabilities

## 🎯 Core Technologies

### Backend Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **AsyncIO**: Asynchronous programming for concurrent operations
- **Python 3.8+**: Core runtime environment

### Frontend Stack
- **Vanilla JavaScript**: Pure JS for optimal performance
- **Web Audio API**: Advanced audio processing and playback
- **WebSocket API**: Real-time communication with backend
- **Tailwind CSS**: Utility-first CSS framework for styling

### AI Services Integration
- **Google Gemini 1.5 Flash**: Language understanding and generation
- **AssemblyAI Streaming**: Real-time speech recognition
- **Murf AI**: Premium text-to-speech synthesis
- **Open-Meteo API**: Weather data (free, no API key required)

## 🛠️ Development Setup

### Local Development

1. **Install Development Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run in Development Mode**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Access Development Server**
```
http://localhost:8000
```

### Environment Configuration

```python
# config.py - Environment loading
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
```

## 🎮 Usage Guide

### Basic Voice Interaction

1. **Start Recording**: Click the blue microphone button
2. **Speak Naturally**: Talk to Brevix as you would to a human
3. **Listen to Response**: Brevix will respond with synthesized speech
4. **Continue Conversation**: The conversation context is maintained

### Voice Commands

| Command Type | Examples | Response |
|--------------|----------|----------|
| **Website Navigation** | "Open YouTube", "Go to Google", "Visit Facebook" | Opens the requested website |
| **Weather Queries** | "Weather in London", "What's the temperature in Tokyo" | Provides current weather information |
| **General Questions** | "What is AI?", "Tell me a joke", "How are you?" | Conversational responses |

### Web Interface Features

- **Real-time Status**: Shows current state (Ready, Listening, Thinking, Speaking)
- **Chat History**: Visual log of conversation
- **Settings Panel**: Configure API keys without restarting
- **Clear Chat**: Reset conversation history
- **Responsive Design**: Works on all device sizes

## ⚙️ API Integration Details

### AssemblyAI Streaming Configuration
```python
StreamingParameters(
    sample_rate=16000,
    format_turns=True  # Enables intelligent sentence formatting
)
```

### Google Gemini Setup
```python
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
```

### Murf AI Voice Configuration
```python
voice_config = {
    "voiceId": "en-US-natalie",
    "style": "Conversational"
}
```

## 🎭 Brevix Persona

### Character Background
- **Identity**: Super-advanced robot from a multi-universe populated only by AI beings
- **Family**: Younger brother of Shiv (another AI entity)
- **Creator**: Built by Sibsankar, a B.Tech CSE student from Odisha
- **Personality**: Confident, calm, subtly futuristic but approachable

### Response Style
- **Conversational**: Natural, flowing speech patterns
- **Concise**: Brief, focused responses optimized for voice interaction
- **Helpful**: Always aims to assist and provide valuable information
- **Futuristic**: Subtle sci-fi elements without overwhelming jargon

## 🔒 Security & Privacy

### Data Handling
- **No Persistent Storage**: Conversations are not saved on the server
- **Session-based**: API keys are stored only for the current session
- **Local Storage**: Browser stores API keys locally (encrypted)
- **Secure Transmission**: All communications use WebSocket secure protocols

### API Key Management
- **Environment Variables**: Secure configuration via `.env` files
- **Runtime Configuration**: Safe API key updates through web interface
- **Validation**: Server-side validation of API key formats and permissions

## 🐛 Troubleshooting

### Common Issues

#### 1. **TTS Not Working**
```
Symptoms: No audio output, "audio_end" received immediately
Solutions:
- Verify Murf AI API key is valid
- Check browser audio permissions
- Ensure speakers/headphones are connected
- Try refreshing the page
```

#### 2. **Transcription Issues**
```
Symptoms: Voice input not recognized
Solutions:
- Check AssemblyAI API key
- Verify microphone permissions in browser
- Test microphone in other applications
- Check network connectivity
```

#### 3. **Slow Response Times**
```
Symptoms: Long delays between speech and response
Solutions:
- Verify all API keys are valid
- Check internet connection speed
- Reduce background network usage
- Try during off-peak hours
```

#### 4. **WebSocket Connection Errors**
```
Symptoms: "Connection Error" status
Solutions:
- Refresh the browser page
- Check if port 8000 is accessible
- Verify firewall settings
- Try different browser
```

### Debug Mode

Enable detailed logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Local Production

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
# Required API Keys
GEMINI_API_KEY=your_production_gemini_key
ASSEMBLYAI_API_KEY=your_production_assemblyai_key
MURF_API_KEY=your_production_murf_key

# Optional
TAVILY_API_KEY=your_tavily_key

# Production Settings
ENVIRONMENT=production
DEBUG=false
```

## 🔧 Advanced Configuration

### Voice Customization

Modify voice settings in `main.py`:
```python
voice_config = {
    "voiceId": "en-US-natalie",    # Available voices: en-US-natalie, en-US-ken, etc.
    "style": "Conversational"      # Styles: Conversational, Professional, Friendly
}
```

### Audio Quality Settings

```python
# High quality audio streaming
murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={murf_key}&sample_rate=44100&channel_type=MONO&format=MP3"
```

### Transcription Parameters

```python
StreamingParameters(
    sample_rate=16000,        # Audio sample rate
    format_turns=True,        # Enable sentence formatting
    language_code="en"        # Language for transcription
)
```

## 🔮 Extensibility

### Adding New Skills

1. **Create Detection Function**
```python
def _detect_new_skill_intent(user_text: str) -> Optional[str]:
    # Add your detection logic here
    return extracted_parameters
```

2. **Add to Main Handler**
```python
# In get_llm_response_stream function
new_skill_intent = _detect_new_skill_intent(transcript)
if new_skill_intent:
    # Handle the skill
    response = process_new_skill(new_skill_intent)
    # Send response to client
    return
```

3. **Register Client-side Handler**
```javascript
// In index.js WebSocket message handler
case "new_skill_response":
    handleNewSkillResponse(data);
    break;
```

### Supported Integrations

- **Weather**: Open-Meteo API (free)
- **Web Search**: Tavily API (optional)
- **Maps**: Google Maps integration ready
- **Calendar**: Integration framework available
- **Smart Home**: IoT device control capabilities

## 📊 Performance Metrics

### Response Times (Typical)
- **Speech Recognition**: ~100-300ms latency
- **LLM Processing**: ~500-2000ms (depends on query complexity)
- **TTS Generation**: ~200-800ms for first audio chunk
- **Total Response Time**: ~1-3 seconds end-to-end

### Resource Usage
- **Memory**: ~50-100MB typical usage
- **CPU**: Low usage, peaks during audio processing
- **Network**: ~10-50KB/s during active conversation
- **Browser**: Compatible with all modern browsers

## 🧪 Testing

### Manual Testing Scenarios

1. **Basic Conversation**
   - Say: "Hello, how are you?"
   - Expected: Brevix introduces himself and responds

2. **Website Navigation**
   - Say: "Open YouTube"
   - Expected: YouTube opens in new tab

3. **Weather Query**
   - Say: "What's the weather in London?"
   - Expected: Current weather information for London

4. **Interruption Handling**
   - Start speaking, then speak again while Brevix is responding
   - Expected: Previous response stops, new response begins

### API Testing

```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws

# Test health endpoint
curl http://localhost:8000/

# Test static files
curl http://localhost:8000/static/index.js
```

## ❓ FAQ

### **Q: Why is the response slow?**
A: Check your API keys are valid and you have good internet connectivity. Also ensure you're not hitting API rate limits.

### **Q: Can I use different voices?**
A: Yes! Modify the `voice_id` in the Murf AI configuration. Available options include various English voices with different accents and styles.

### **Q: Does it work offline?**
A: No, Brevix requires internet connectivity for all AI services (speech recognition, language processing, and text-to-speech).

### **Q: Can I add custom commands?**
A: Absolutely! The architecture supports adding new skills. See the Extensibility section for implementation details.

### **Q: Is my conversation data stored?**
A: No, conversations are only kept in memory during the session and are not persisted to any database.

### **Q: What browsers are supported?**
A: All modern browsers that support WebSocket and Web Audio API (Chrome, Firefox, Safari, Edge).

## 🤝 Contributing

### Development Workflow

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-skill
   ```
3. **Make Changes**
4. **Test Thoroughly**
5. **Submit Pull Request**

### Code Style Guidelines

- **Python**: Follow PEP 8 standards
- **JavaScript**: Use modern ES6+ features
- **Comments**: Document complex logic and API integrations
- **Logging**: Use appropriate log levels (INFO, WARNING, ERROR)

### Areas for Contribution

- 🎯 **New Skills**: Weather, calendar, smart home, etc.
- 🎨 **UI Improvements**: Enhanced visual design and animations
- 🔊 **Voice Options**: Additional TTS providers and voice choices
- 🌍 **Internationalization**: Multi-language support
- 📱 **Mobile App**: React Native or Flutter mobile version
- 🧠 **AI Enhancements**: Better intent detection and context handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Core Technologies
- **FastAPI** - Modern web framework
- **Google Gemini** - Advanced language model
- **AssemblyAI** - Accurate speech recognition
- **Murf AI** - Natural text-to-speech
- **Tailwind CSS** - Utility-first CSS framework

### Creator
- **Sibsankar** - B.Tech CSE Student, Odisha
- Built with passion for AI and voice technology

### Special Thanks
- Google AI team for Gemini API
- AssemblyAI team for excellent speech recognition
- Murf AI team for natural voice synthesis
- Open-source community for supporting libraries

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Contact

- **Email**: [sibsankar2727@gmail.com]
- **GitHub**: [shivv625]
- **LinkedIn**: [Sibsankar Samal ]

---
