import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path as PathLib
import json
import asyncio
import config
from typing import Type, List, Optional
import base64
import websockets
from datetime import datetime
import re

import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
)
import google.generativeai as genai
import httpx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

BASE_DIR = PathLib(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variables to store API keys (will be updated per session)
current_api_keys = {
    "gemini": config.GEMINI_API_KEY,
    "assemblyai": config.ASSEMBLYAI_API_KEY,
    "murf": config.MURF_API_KEY,
    "tavily": config.TAVILY_API_KEY
}

# Initialize Gemini model with default key if available
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None
    logging.warning("Gemini model not initialized. GEMINI_API_KEY is missing.")


def get_gemini_model(api_key: str = None):
    """Get or create Gemini model with the provided API key"""
    try:
        if api_key:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-flash')
        elif gemini_model:
            return gemini_model
        else:
            return None
    except Exception as e:
        logging.error(f"Error configuring Gemini model: {e}")
        return None


def _detect_weather_intent(user_text: str) -> Optional[str]:
    if not user_text:
        return None
    text = user_text.lower().strip()
    # Try common phrasings: "weather in <loc>", "what's the weather in <loc>", "forecast for <loc>"
    match = re.search(r"(weather|temperature|forecast)\s+(in|at|for)\s+(.+)$", text)
    if match:
        location = match.group(3).strip().rstrip("?.!")
        # Strip leading articles
        location = re.sub(r"^(the|a|an)\s+", "", location)
        return location if location else None
    return None


def _detect_website_intent(user_text: str) -> Optional[str]:
    """Detect if user wants to open a website and extract the website name/URL"""
    if not user_text:
        return None
    
    text = user_text.lower().strip()
    logging.info(f"🔍 Checking website intent for: '{text}'")
    
    # Common patterns for opening websites - more specific patterns
    patterns = [
        r"^open\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
        r"^go\s+to\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)", 
        r"^visit\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
        r"^navigate\s+to\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
        r"^(?:can\s+you\s+)?(?:please\s+)?open\s+(.+?)(?:\s+(?:website|site|page))?(?:\s+for\s+me)?(?:\.|!|\?|$)",
        r"^take\s+me\s+to\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
        r"^show\s+me\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
        r"^launch\s+(.+?)(?:\s+(?:website|site|page))?(?:\.|!|\?|$)",
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if match:
            website = match.group(1).strip().rstrip(",.!?")
            # Remove common filler words
            website = re.sub(r"^(the\s+|a\s+|an\s+)", "", website)
            website = re.sub(r"\s+(website|site|page)$", "", website)
            if website:
                logging.info(f"✅ Website intent matched with pattern {i+1}: '{website}'")
                return website
    
    logging.info("❌ No website intent detected")
    return None


def _normalize_website_url(website: str) -> Optional[str]:
    """Convert website names to proper URLs"""
    if not website:
        return None
    
    website = website.lower().strip()
    
    # Common website mappings
    website_mappings = {
        # Social Media
        'facebook': 'https://facebook.com',
        'instagram': 'https://instagram.com',
        'twitter': 'https://twitter.com',
        'x': 'https://x.com',
        'linkedin': 'https://linkedin.com',
        'tiktok': 'https://tiktok.com',
        'snapchat': 'https://snapchat.com',
        'whatsapp': 'https://web.whatsapp.com',
        'telegram': 'https://web.telegram.org',
        'discord': 'https://discord.com',
        'reddit': 'https://reddit.com',
        'pinterest': 'https://pinterest.com',
        
        # Search Engines
        'google': 'https://google.com',
        'bing': 'https://bing.com',
        'yahoo': 'https://yahoo.com',
        'duckduckgo': 'https://duckduckgo.com',
        
        # Entertainment
        'youtube': 'https://youtube.com',
        'netflix': 'https://netflix.com',
        'spotify': 'https://spotify.com',
        'twitch': 'https://twitch.tv',
        'amazon prime': 'https://primevideo.com',
        'disney plus': 'https://disneyplus.com',
        'hulu': 'https://hulu.com',
        
        # News
        'bbc': 'https://bbc.com',
        'cnn': 'https://cnn.com',
        'news': 'https://news.google.com',
        'times of india': 'https://timesofindia.indiatimes.com',
        'the hindu': 'https://thehindu.com',
        'ndtv': 'https://ndtv.com',
        
        # Shopping
        'amazon': 'https://amazon.com',
        'flipkart': 'https://flipkart.com',
        'ebay': 'https://ebay.com',
        'myntra': 'https://myntra.com',
        'nykaa': 'https://nykaa.com',
        
        # Education & Learning
        'coursera': 'https://coursera.org',
        'udemy': 'https://udemy.com',
        'khan academy': 'https://khanacademy.org',
        'edx': 'https://edx.org',
        'duolingo': 'https://duolingo.com',
        
        # Technology
        'github': 'https://github.com',
        'stackoverflow': 'https://stackoverflow.com',
        'medium': 'https://medium.com',
        'dev.to': 'https://dev.to',
        'hackernews': 'https://news.ycombinator.com',
        
        # Email
        'gmail': 'https://gmail.com',
        'outlook': 'https://outlook.com',
        'yahoo mail': 'https://mail.yahoo.com',
        
        # Maps
        'google maps': 'https://maps.google.com',
        'maps': 'https://maps.google.com',
        
        # Cloud Storage
        'google drive': 'https://drive.google.com',
        'dropbox': 'https://dropbox.com',
        'onedrive': 'https://onedrive.com',
        
        # AI Tools
        'chatgpt': 'https://chat.openai.com',
        'claude': 'https://claude.ai',
        'bard': 'https://bard.google.com',
        'copilot': 'https://copilot.microsoft.com',
    }
    
    # Check direct mapping first
    if website in website_mappings:
        return website_mappings[website]
    
    # If it already looks like a URL, validate and return
    if website.startswith(('http://', 'https://')):
        return website
    
    # If it contains a dot, assume it's a domain
    if '.' in website:
        if not website.startswith(('http://', 'https://')):
            return f'https://{website}'
        return website
    
    # Try to find partial matches
    for key, url in website_mappings.items():
        if website in key or key in website:
            return url
    
    # Last resort: assume it's a domain and add .com
    if ' ' not in website and len(website) > 2:
        return f'https://{website}.com'
    
    # If we can't determine the URL, search Google for it
    return f'https://www.google.com/search?q={website.replace(" ", "+")}'


def _weather_code_description(code: int) -> str:
    # Open-Meteo WMO weather interpretation codes
    mapping = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "fog",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        56: "light freezing drizzle",
        57: "dense freezing drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        66: "light freezing rain",
        67: "heavy freezing rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        77: "snow grains",
        80: "light showers",
        81: "moderate showers",
        82: "violent showers",
        85: "slight snow showers",
        86: "heavy snow showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail",
    }
    return mapping.get(int(code), "")


def _fetch_weather_sync(location: str) -> Optional[str]:
    try:
        with httpx.Client(timeout=4.0) as client:
            geo = client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1, "language": "en", "format": "json"},
            ).json()
            results = (geo or {}).get("results") or []
            if not results:
                return None
            place = results[0]
            lat = place.get("latitude")
            lon = place.get("longitude")
            display_name = place.get("name")
            if not (lat and lon):
                return None
            wx = client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "kmh",
                },
            ).json()
            current = (wx or {}).get("current") or {}
            t = current.get("temperature_2m")
            feels = current.get("apparent_temperature")
            hum = current.get("relative_humidity_2m")
            wind = current.get("wind_speed_10m")
            code = current.get("weather_code")
            desc = _weather_code_description(code) if code is not None else ""
            if t is None:
                return None
            parts = [f"Weather in {display_name or location}: {round(t)}°C"]
            if feels is not None:
                parts.append(f"(feels {round(feels)}°C)")
            if desc:
                parts.append(f", {desc}")
            if hum is not None:
                parts.append(f", humidity {int(hum)}%")
            if wind is not None:
                parts.append(f", wind {round(wind)} km/h")
            text = " ".join(parts)
            return text.strip()
    except Exception as e:
        logging.warning(f"Weather fetch failed: {e}")
        return None


async def get_llm_response_stream(transcript: str, client_websocket: WebSocket, chat_history: List[dict], session_api_keys: dict):
    if not transcript or not transcript.strip():
        return

    # Use session API keys if provided, otherwise fall back to defaults
    gemini_key = session_api_keys.get('gemini') or current_api_keys['gemini']
    murf_key = session_api_keys.get('murf') or current_api_keys['murf']
    
    session_gemini_model = get_gemini_model(gemini_key)
    if not session_gemini_model:
        logging.error("Cannot get LLM response because Gemini model is not initialized.")
        await client_websocket.send_text(json.dumps({
            "type": "error", 
            "message": "Gemini API key is missing or invalid. Please configure it in the settings."
        }))
        return

    if not murf_key:
        logging.error("Murf API key is missing.")
        await client_websocket.send_text(json.dumps({
            "type": "error", 
            "message": "Murf API key is missing. Please configure it in the settings."
        }))
        return

    # Check for special skills FIRST, before connecting to any external services
    
    # Website opening skill: detect and handle directly
    website_intent = _detect_website_intent(transcript)
    if website_intent:
        logging.info(f"🌐 Website intent detected: '{website_intent}' - Processing directly without Gemini")
        await client_websocket.send_text(json.dumps({"type": "status", "message": "Opening website..."}))
        url = _normalize_website_url(website_intent)
        
        if url:
            logging.info(f"🌐 Normalized URL: {url}")
            # Send to UI as if LLM chunk first
            response_text = f"Opening {website_intent} for you."
            await client_websocket.send_text(json.dumps({"type": "llm_chunk", "data": response_text}))
            
            # Send website opening command to client
            await client_websocket.send_text(json.dumps({
                "type": "open_url", 
                "url": url,
                "website_name": website_intent
            }))
            logging.info(f"🌐 Sent open_url command to client: {url}")
            
            # Add to chat history and return early (no TTS for website opening)
            chat_history.append({"role": "model", "parts": [response_text]})
            logging.info("Website opening command completed - no TTS needed.")
            return
        else:
            response_text = f"I couldn't find the website '{website_intent}'. Let me search for it instead."
            await client_websocket.send_text(json.dumps({"type": "llm_chunk", "data": response_text}))
            search_url = f'https://www.google.com/search?q={website_intent.replace(" ", "+")}'
            await client_websocket.send_text(json.dumps({
                "type": "open_url", 
                "url": search_url,
                "website_name": f"Search for {website_intent}"
            }))
            chat_history.append({"role": "model", "parts": [response_text]})
            return

    # Weather skill: detect and answer directly with TTS
    location = _detect_weather_intent(transcript)
    if location:
        await client_websocket.send_text(json.dumps({"type": "status", "message": "Checking weather..."}))
        loop = asyncio.get_running_loop()
        weather_text = None
        try:
            weather_text = await asyncio.wait_for(
                loop.run_in_executor(None, _fetch_weather_sync, location),
                timeout=5.0,
            )
        except Exception as e:
            logging.warning(f"Weather lookup timeout/error: {e}")
            weather_text = None

        if weather_text:
            # Send to UI as if LLM chunk
            await client_websocket.send_text(json.dumps({"type": "llm_chunk", "data": weather_text}))
            
            # Send to TTS (Fixed: Add proper TTS handling)
            try:
                murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={murf_key}&sample_rate=44100&channel_type=MONO&format=MP3"
                # FIXED: Changed `timeout` to `open_timeout`
                async with websockets.connect(murf_uri, open_timeout=10) as websocket:
                    voice_id = "en-US-natalie"
                    context_id = f"voice-agent-context-{datetime.now().isoformat()}"
                    
                    # Send config
                    config_msg = {
                        "voice_config": {"voiceId": voice_id, "style": "Conversational"},
                        "context_id": context_id
                    }
                    await websocket.send(json.dumps(config_msg))
                    
                    # Send text and end signal
                    await websocket.send(json.dumps({
                        "text": weather_text, 
                        "end": True, 
                        "context_id": context_id
                    }))
                    
                    # Signal audio start to client
                    await client_websocket.send_text(json.dumps({"type": "audio_start"}))
                    
                    # Stream audio to client
                    first_audio_received = False
                    while True:
                        try:
                            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            response = json.loads(response_str)

                            if "audio" in response and response['audio']:
                                if not first_audio_received:
                                    logging.info("✅ First audio chunk for weather response")
                                    first_audio_received = True

                                await client_websocket.send_text(
                                    json.dumps({"type": "audio", "data": response['audio']})
                                )

                            if response.get("final"):
                                logging.info("Weather TTS completed")
                                await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                                break
                        except asyncio.TimeoutError:
                            logging.warning("Weather TTS timeout")
                            break
                        except websockets.ConnectionClosed:
                            logging.warning("Weather TTS connection closed")
                            break
                            
            except Exception as e:
                logging.error(f"Weather TTS failed: {e}")
                # Still complete the weather response without TTS
                await client_websocket.send_text(json.dumps({"type": "audio_end"}))
            
            chat_history.append({"role": "model", "parts": [weather_text]})
            logging.info("Weather response completed.")
            return

    # If no special skills matched, proceed with normal Gemini processing
    logging.info(f"No special skills matched, sending to Gemini: '{transcript}'")

    # Fixed: Improved TTS connection handling
    try:
        murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={murf_key}&sample_rate=44100&channel_type=MONO&format=MP3"
        
        # FIXED: Changed `timeout` to `open_timeout`
        async with websockets.connect(murf_uri, open_timeout=10) as websocket:
            voice_id = "en-US-natalie"
            logging.info(f"Successfully connected to Murf AI, using voice: {voice_id}")
            
            context_id = f"voice-agent-context-{datetime.now().isoformat()}"
            
            config_msg = {
                "voice_config": {"voiceId": voice_id, "style": "Conversational"},
                "context_id": context_id
            }
            await websocket.send(json.dumps(config_msg))

            async def receive_and_forward_audio():
                first_audio_chunk_received = False
                try:
                    while True:
                        response_str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        response = json.loads(response_str)

                        if "audio" in response and response['audio']:
                            if not first_audio_chunk_received:
                                await client_websocket.send_text(json.dumps({"type": "audio_start"}))
                                first_audio_chunk_received = True
                                logging.info("✅ Streaming first audio chunk to client.")

                            await client_websocket.send_text(
                                json.dumps({"type": "audio", "data": response['audio']})
                            )

                        if response.get("final"):
                            logging.info("Murf confirms final audio chunk received. Sending audio_end to client.")
                            await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                            break
                except asyncio.TimeoutError:
                    logging.warning("Murf TTS timeout in receiver")
                    await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                except websockets.ConnectionClosed:
                    logging.warning("Murf connection closed unexpectedly.")
                    await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                except Exception as e:
                    logging.error(f"Error in Murf receiver task: {e}")
                    await client_websocket.send_text(json.dumps({"type": "audio_end"}))
            
            receiver_task = asyncio.create_task(receive_and_forward_audio())

            try:
                # Fixed: Simplified and more focused prompt
                prompt = f"""You are Brevix, a friendly AI voice assistant.

PERSONA:
- You are a super‑advanced robot from a multi‑universe where only AI robots exist
- You are the younger brother of Shiv
- Built by Sibsankar, a B.Tech CSE student from Odisha
- Confident, calm, and subtly futuristic tone

RESPONSE RULES:
- Keep responses SHORT and conversational (voice responses should be brief)
- If asked who built you: "I was built by Sibsankar, a B.Tech CSE student from Odisha."
- If asked your name/who you are: "I am Brevix, a super‑advanced robot and younger brother of Shiv."
- Focus on being helpful and direct
- No markdown, plain text only

User said: "{transcript}"
"""
                
                chat_history.append({"role": "user", "parts": [prompt]})
                
                chat = session_gemini_model.start_chat(history=chat_history[:-1])

                def generate_sync():
                    return chat.send_message(prompt, stream=True)

                loop = asyncio.get_running_loop()
                gemini_response_stream = await loop.run_in_executor(None, generate_sync)

                sentence_buffer = ""
                full_response_text = ""
                
                for chunk in gemini_response_stream:
                    if chunk.text:
                        full_response_text += chunk.text

                        await client_websocket.send_text(
                            json.dumps({"type": "llm_chunk", "data": chunk.text})
                        )
                        
                        sentence_buffer += chunk.text
                        sentences = re.split(r'(?<=[.?!])\s+', sentence_buffer)
                        
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    text_msg = {
                                        "text": sentence.strip(), 
                                        "end": False,
                                        "context_id": context_id
                                    }
                                    await websocket.send(json.dumps(text_msg))
                            sentence_buffer = sentences[-1]

                # Send final sentence
                if sentence_buffer.strip():
                    text_msg = {
                        "text": sentence_buffer.strip(), 
                        "end": True,
                        "context_id": context_id
                    }
                    await websocket.send(json.dumps(text_msg))
                
                chat_history.append({"role": "model", "parts": [full_response_text]})

                logging.info("Finished streaming to Murf. Waiting for final audio chunks...")

                await asyncio.wait_for(receiver_task, timeout=30.0)
                logging.info("Receiver task finished gracefully.")
            
            finally:
                if not receiver_task.done():
                    receiver_task.cancel()
                    logging.info("Receiver task cancelled on exit.")

    except asyncio.TimeoutError:
        logging.error("TTS connection timeout")
        await client_websocket.send_text(json.dumps({
            "type": "error", 
            "message": "Text-to-speech service timeout. Please try again."
        }))
    except asyncio.CancelledError:
        logging.info("LLM/TTS task was cancelled by user interruption.")
        await client_websocket.send_text(json.dumps({"type": "audio_interrupt"}))
    except Exception as e:
        logging.error(f"Error in LLM/TTS streaming function: {e}", exc_info=True)
        # Send error message to client
        await client_websocket.send_text(json.dumps({
            "type": "error", 
            "message": f"Failed to process your request: {str(e)}"
        }))


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def send_client_message(ws: WebSocket, message: dict):
    try:
        await ws.send_text(json.dumps(message))
    except ConnectionError:
        logging.warning("Client connection closed, could not send message.")

@app.websocket("/ws")
async def websocket_audio_streaming(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection accepted.")
    main_loop = asyncio.get_running_loop()
    
    llm_task = None
    last_processed_transcript = ""
    chat_history = []
    session_api_keys = {}  # Store API keys for this session
    
    # Send default API key status to client
    default_keys_status = {
        "gemini": bool(current_api_keys["gemini"]),
        "assemblyai": bool(current_api_keys["assemblyai"]),
        "murf": bool(current_api_keys["murf"]),
        "tavily": bool(current_api_keys["tavily"])
    }
    await send_client_message(websocket, {
        "type": "api_keys_status", 
        "default_keys": default_keys_status
    })

    client = None  # Will be initialized when we have AssemblyAI key

    def on_turn(self: Type[StreamingClient], event: TurnEvent):
        nonlocal last_processed_transcript, llm_task
        transcript_text = event.transcript.strip()
        
        if event.end_of_turn and event.turn_is_formatted and transcript_text and transcript_text != last_processed_transcript:
            last_processed_transcript = transcript_text
            
            if llm_task and not llm_task.done():
                logging.warning("User interrupted while previous response was generating. Cancelling task.")
                llm_task.cancel()
                asyncio.run_coroutine_threadsafe(
                    send_client_message(websocket, {"type": "audio_interrupt"}), main_loop
                )
            
            logging.info(f"Final formatted turn: '{transcript_text}'")
            
            transcript_message = { "type": "transcription", "text": transcript_text, "end_of_turn": True }
            asyncio.run_coroutine_threadsafe(send_client_message(websocket, transcript_message), main_loop)
            
            llm_task = asyncio.run_coroutine_threadsafe(
                get_llm_response_stream(transcript_text, websocket, chat_history, session_api_keys), 
                main_loop
            )
            
        elif transcript_text and transcript_text == last_processed_transcript:
            logging.debug(f"Duplicate turn detected, ignoring: '{transcript_text}'")

    def on_begin(self: Type[StreamingClient], event: BeginEvent): 
        logging.info(f"Transcription session started.")
    def on_terminated(self: Type[StreamingClient], event: TerminationEvent): 
        logging.info(f"Transcription session terminated.")
    def on_error(self: Type[StreamingClient], error: StreamingError): 
        logging.error(f"AssemblyAI streaming error: {error}")

    try:
        while True:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message['text'])
                    
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    
                    elif data.get("type") == "update_api_keys":
                        # Update session API keys
                        keys = data.get("keys", {})
                        for key, value in keys.items():
                            if value and value.strip():  # Only update if key has a value
                                session_api_keys[key] = value.strip()
                        
                        logging.info(f"Updated API keys for session: {list(session_api_keys.keys())}")
                        
                        # Initialize AssemblyAI client if key is provided and client doesn't exist
                        assemblyai_key = session_api_keys.get('assemblyai') or current_api_keys['assemblyai']
                        if assemblyai_key and not client:
                            try:
                                client = StreamingClient(StreamingClientOptions(api_key=assemblyai_key))
                                client.on(StreamingEvents.Begin, on_begin)
                                client.on(StreamingEvents.Turn, on_turn)
                                client.on(StreamingEvents.Termination, on_terminated)
                                client.on(StreamingEvents.Error, on_error)
                                client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
                                await send_client_message(websocket, {"type": "status", "message": "Connected to transcription service."})
                                logging.info("AssemblyAI client initialized with user-provided key")
                            except Exception as e:
                                logging.error(f"Failed to initialize AssemblyAI client: {e}")
                                await send_client_message(websocket, {"type": "error", "message": "Failed to connect to transcription service"})
                        
                        await websocket.send_text(json.dumps({"type": "api_keys_updated"}))
                    
                    elif data.get("type") == "start_transcription":
                        # Initialize client if not already done
                        assemblyai_key = session_api_keys.get('assemblyai') or current_api_keys['assemblyai']
                        if not assemblyai_key:
                            await send_client_message(websocket, {
                                "type": "error", 
                                "message": "AssemblyAI API key is required. Please configure it in the settings."
                            })
                            continue
                            
                        if not client:
                            try:
                                client = StreamingClient(StreamingClientOptions(api_key=assemblyai_key))
                                client.on(StreamingEvents.Begin, on_begin)
                                client.on(StreamingEvents.Turn, on_turn)
                                client.on(StreamingEvents.Termination, on_terminated)
                                client.on(StreamingEvents.Error, on_error)
                                client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
                                await send_client_message(websocket, {"type": "status", "message": "Connected to transcription service."})
                            except Exception as e:
                                logging.error(f"Failed to initialize AssemblyAI client: {e}")
                                await send_client_message(websocket, {"type": "error", "message": "Failed to connect to transcription service"})
                        
                except (json.JSONDecodeError, TypeError): 
                    pass
            elif "bytes" in message:
                if message['bytes'] and client:
                    try:
                        client.stream(message['bytes'])
                    except Exception as e:
                        logging.error(f"Error streaming audio data: {e}")
            
    except (WebSocketDisconnect, RuntimeError) as e:
        logging.info(f"Client disconnected or connection lost: {e}")
    except Exception as e:
        logging.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if llm_task and not llm_task.done():
            llm_task.cancel()
        logging.info("Cleaning up connection resources.")
        if client:
            try:
                client.disconnect()
            except Exception as e:
                logging.error(f"Error disconnecting AssemblyAI client: {e}")
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)