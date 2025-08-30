# Brevix - AI Voice Assistant

> **Real-time voice assistant powered by cutting-edge AI technologies**

Brevix is an intelligent voice-powered conversational agent that combines speech recognition, natural language processing, and text-to-speech synthesis for seamless voice interactions.

![Brevix Demo](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

## ✨ Features

- 🎤 **Real-Time Speech Recognition** - Live transcription via AssemblyAI
- 🧠 **Intelligent Conversations** - Powered by Google Gemini 1.5 Flash  
- 🔊 **Natural Text-to-Speech** - High-quality voice synthesis with Murf AI
- 🌐 **Smart Skills** - Website navigation, weather info, web search
- 🎨 **Modern UI** - Glassmorphism design with real-time status indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser with microphone access
- Internet connection

### Installation

1. **Clone and install**
```bash
git clone https://github.com/yourusername/brevix-voice-assistant.git
cd brevix-voice-assistant
pip install -r requirements.txt
```

2. **Configure API Keys**

Create `.env` file:
```env
GEMINI_API_KEY=your_google_gemini_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key  
MURF_API_KEY=your_murf_ai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

3. **Run Application**
```bash
python main.py
```

4. **Access Brevix**
```
http://localhost:8000
```

## 🔧 API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Google Gemini** | Language Model | [Google AI Studio](https://makersuite.google.com/) |
| **AssemblyAI** | Speech Recognition | [AssemblyAI Console](https://www.assemblyai.com/) |
| **Murf AI** | Text-to-Speech | [Murf AI Platform](https://murf.ai/) |
| **Tavily** | Web Search (Optional) | [Tavily API](https://tavily.com/) |

## 🏗️ Architecture

```
Browser Audio → WebSocket → AssemblyAI → Transcript
     ↓
Gemini AI → Response → Murf TTS → Audio Stream → Speaker
```

## 📁 Project Structure

```
brevix-voice-assistant/
├── main.py              # FastAPI app & WebSocket handlers
├── config.py            # Configuration loading
├── requirements.txt     # Dependencies
├── static/index.js      # Frontend JavaScript  
├── templates/index.html # Web interface
└── .env                 # API keys (create this)
```

## 🎮 Usage

### Voice Commands
- **Websites**: "Open YouTube", "Go to Google"
- **Weather**: "Weather in London", "Temperature in Tokyo"  
- **General**: "What is AI?", "Tell me a joke"

### Web Interface
- Click microphone to start/stop recording
- Real-time chat display
- Settings panel for API configuration
- Status indicators (Ready, Listening, Thinking, Speaking)

## 🎭 Brevix Persona

- **Identity**: Super-advanced robot from AI-only multi-universe
- **Creator**: Built by Sibsankar (B.Tech CSE student, Odisha)
- **Personality**: Confident, calm, subtly futuristic
- **Style**: Conversational and helpful responses

## 🐛 Troubleshooting

### Common Issues

**TTS Not Working**
- Verify Murf AI API key
- Check browser audio permissions
- Refresh page

**No Transcription**  
- Check AssemblyAI API key
- Verify microphone permissions
- Test mic in other apps

**Slow Responses**
- Verify all API keys are valid
- Check internet connection
- Try during off-peak hours

## 🔧 Development

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Skills

1. Create detection function in `main.py`
2. Add handler in `get_llm_response_stream()`
3. Register client-side handler in `index.js`

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```env
GEMINI_API_KEY=production_key
ASSEMBLYAI_API_KEY=production_key
MURF_API_KEY=production_key
ENVIRONMENT=production
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

### Areas for Contribution
- 🎯 New skills (calendar, smart home)
- 🎨 UI improvements  
- 🔊 Additional voice options
- 🌍 Multi-language support
- 📱 Mobile app version

## 📊 Performance

- **Response Time**: 1-3 seconds end-to-end
- **Memory Usage**: ~50-100MB
- **Network**: ~10-50KB/s during conversation
- **Browser**: All modern browsers supported

## 🔒 Security

- No conversation data stored
- API keys stored locally/session-based
- Secure WebSocket communication
- No persistent data collection

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

**Technologies**: FastAPI, Google Gemini, AssemblyAI, Murf AI, Tailwind CSS

**Creator**: Sibsankar - B.Tech CSE Student, Odisha

---

**Made with ❤️ by Sibsankar | Powered by AI**
