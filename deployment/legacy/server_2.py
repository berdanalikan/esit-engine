"""
ESİT Smart Assistant Server - Simplified Real-time Support System
"""

import os
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from smart_assistant import SmartAssistant, get_smart_assistant

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = FastAPI(title="ESİT Smart Assistant API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend
web_dir = Path.cwd() / "esit-website"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")

# Request models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

# Initialize assistant
PDF_PATH = str(Path.cwd() / "Esit_ECI_User_Manual_Automatic_ENG_v1_7 kopyası.pdf")


@app.get("/health")
async def health():
    return {"status": "ok", "system": "ESİT Smart Assistant"}


# Initialize smart assistant
smart_assistant_instance = None

def initialize_smart_assistant():
    """Initialize smart assistant"""
    global smart_assistant_instance
    if smart_assistant_instance is None:
        smart_assistant_instance = get_smart_assistant(PDF_PATH)
    return smart_assistant_instance

@app.post("/chat")
async def chat(req: ChatRequest):
    """Ana sohbet endpoint'i - Smart Assistant sistemi"""
    
    try:
        # Smart assistant'ı başlat
        assistant = initialize_smart_assistant()
        
        # Akıllı yanıt üret
        result = await assistant.generate_smart_response(req.message)
        
        return {
            "response": result.get("response", ""),
            "type": result.get("type", "ai_response"),
            "has_pdf_context": result.get("has_pdf_context", False),
            "search_results": result.get("search_results", {}),
            "problem_analysis": result.get("problem_analysis", {}),
            "conversation_id": req.conversation_id or "default",
            "success": True
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen tekrar deneyin.",
            "type": "error",
            "error": str(e),
            "success": False
        }

@app.post("/reset")
async def reset_conversation():
    """Konuşmayı sıfırla"""
    try:
        assistant = initialize_smart_assistant()
        assistant.conversation_history = []
        return {"success": True, "message": "Konuşma geçmişi sıfırlandı"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    """Text-to-Speech endpoint'i"""
    
    try:
        # OpenAI TTS direkt kullan
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=req.voice,
            input=req.text[:500]  # Limit text length
        )
        
        audio_content = response.content
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
            
    except Exception as e:
        return {"error": f"TTS error: {str(e)}"}


@app.post("/reset")
async def reset_conversation():
    """Konuşmayı sıfırla"""
    
    try:
        assistant = get_guided_assistant(PDF_PATH)
        assistant.reset_conversation()
        return {"success": True, "message": "Conversation reset"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/status")
async def get_status():
    """Sistem durumu"""
    
    try:
        assistant = get_guided_assistant(PDF_PATH)
        summary = assistant.get_conversation_summary()
        
        return {
            "system": "ESİT Smart Assistant",
            "pdf_loaded": Path(PDF_PATH).exists(),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "conversation": summary,
            "features": {
                "problem_detection": True,
                "pdf_search": True,
                "tts": True,
                "realtime_chat": True
            }
        }
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Ana sayfa - basit test arayüzü"""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>ESİT Smart Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; margin: 20px 0; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
        .user { background: #007bff; color: white; text-align: right; }
        .assistant { background: #f8f9fa; border: 1px solid #dee2e6; }
        .input-group { display: flex; gap: 10px; }
        .input-group input { flex: 1; padding: 10px; }
        .input-group button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; }
        .status { background: #e9ecef; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <h1>🤖 ESİT Smart Assistant</h1>
    <p>Akıllı teknik destek sistemi - Sorunlarınızı anlar ve PDF'den çözüm bulur</p>
    
    <div class="status" id="status">Sistem hazırlanıyor...</div>
    
    <div class="chat-container" id="chatContainer"></div>
    
    <div class="input-group">
        <input type="text" id="messageInput" placeholder="Sorunuzu yazın... (örn: ECI sistemim çalışmıyor)" />
        <button onclick="sendMessage()">Gönder</button>
        <button onclick="resetChat()">Sıfırla</button>
    </div>
    
    <script>
        let chatContainer = document.getElementById('chatContainer');
        let messageInput = document.getElementById('messageInput');
        let statusDiv = document.getElementById('status');
        
        // Sistem durumunu kontrol et
        async function checkStatus() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                
                let statusText = `✅ PDF: ${data.pdf_loaded ? 'Yüklü' : 'Yok'} | `;
                statusText += `🔑 OpenAI: ${data.openai_configured ? 'Yapılandırılmış' : 'Eksik'} | `;
                statusText += `💬 Mesaj: ${data.conversation?.message_count || 0}`;
                
                statusDiv.textContent = statusText;
                statusDiv.style.background = data.openai_configured ? '#d4edda' : '#f8d7da';
                
            } catch (e) {
                statusDiv.textContent = '❌ Sistem hatası: ' + e.message;
                statusDiv.style.background = '#f8d7da';
            }
        }
        
        function addMessage(content, isUser = false) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'assistant');
            div.textContent = content;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            messageInput.value = '';
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await res.json();
                
                let response = data.response;
                if (data.problem_detected) {
                    response += ` [${data.product} sorunu tespit edildi]`;
                }
                if (data.has_pdf_context) {
                    response += ` [PDF'den bilgi kullanıldı]`;
                }
                
                addMessage(response);
                
                // TTS çal
                if (data.success && data.response) {
                    playTTS(data.response);
                }
                
            } catch (e) {
                addMessage('Hata: ' + e.message);
            }
            
            checkStatus();
        }
        
        async function playTTS(text) {
            try {
                const res = await fetch('/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                if (res.ok) {
                    const audioBlob = await res.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                }
            } catch (e) {
                console.warn('TTS failed:', e);
            }
        }
        
        async function resetChat() {
            try {
                await fetch('/reset', { method: 'POST' });
                chatContainer.innerHTML = '';
                addMessage('Konuşma sıfırlandı. Size nasıl yardımcı olabilirim?');
                checkStatus();
            } catch (e) {
                addMessage('Sıfırlama hatası: ' + e.message);
            }
        }
        
        // Enter key support
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Başlangıç
        checkStatus();
        addMessage('Merhaba! ESİT Smart Assistant\'a hoş geldiniz. Sorunlarınızı anlayıp PDF kılavuzundan çözüm bulurum. Size nasıl yardımcı olabilirim?');
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html)