"""
ESİT Technical Support AI - Simple Web Server
Fine-tuned model için basitleştirilmiş web sunucusu
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simple_ai import get_simple_ai

# Initialize FastAPI
app = FastAPI(
    title="ESİT Technical Support AI",
    description="Fine-tuned model ile teknik destek",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

@app.get("/")
async def root():
    """Ana sayfa"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESİT Teknik Destek AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 800px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 90vh;
        }
        
        .header {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 25px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 8px;
        }
        
        .header .badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            display: inline-block;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1rem;
        }
        
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .messages {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }
        
        .message {
            display: flex;
            gap: 12px;
            max-width: 85%;
            animation: fadeIn 0.3s ease-in;
        }
        
        .user-message {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .bot-message {
            align-self: flex-start;
        }
        
        .avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        }
        
        .user-message .avatar {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        .bot-message .avatar {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
        }
        
        .message-content {
            background: #f8fafc;
            padding: 14px 18px;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        
        .user-message .message-content {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .bot-message .message-content {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
        }
        
        .category-badge {
            background: #fef3c7;
            color: #92400e;
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            margin-top: 8px;
            display: inline-block;
            border: 1px solid #fcd34d;
        }
        
        .input-area {
            padding: 25px;
            border-top: 1px solid #e2e8f0;
            background: #f8fafc;
        }
        
        .input-container {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .message-input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }
        
        .message-input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .send-button {
            width: 55px;
            height: 55px;
            border: none;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            font-size: 1.3rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .send-button:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }
        
        .send-button:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 12px;
        }
        
        .control-button {
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            background: #e5e7eb;
            color: #6b7280;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.85rem;
        }
        
        .control-button:hover {
            background: #d1d5db;
            transform: translateY(-1px);
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid #e5e7eb;
            border-top: 2px solid #4f46e5;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container { height: 100vh; border-radius: 0; }
            .header { padding: 18px; }
            .messages { padding: 18px; }
            .input-area { padding: 18px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge">🧠 Fine-tuned Model</div>
            <h1>🤖 ESİT Teknik Destek AI</h1>
            <p>ECI kullanma kılavuzu ile eğitilmiş özel model</p>
        </div>
        
        <div class="chat-area">
            <div id="messages" class="messages">
                <div class="message bot-message">
                    <div class="avatar">🤖</div>
                    <div class="message-content">
                        👋 Merhaba! ESİT Teknik Destek AI'ya hoş geldiniz.
                        
                        🧠 **Fine-tuned model** ile güçlendirilmiş sistem
                        ECI kullanma kılavuzu ile eğitilmiş özel modelimiz sayesinde hızlı ve doğru yanıtlar alabilirsiniz.
                        
                        **Örnek sorular:**
                        • "ECI cihazım açılmıyor, ne yapmalıyım?"
                        • "Sıfır kalibrasyonu nasıl yapılır?"
                        • "Load cell bağlantı hatası alıyorum"
                        • "Menü 2.5'e nasıl girerim?"
                        • "Ekranda E002 hatası görüyorum"
                    </div>
                </div>
            </div>
        </div>
        
        <div class="input-area">
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    class="message-input" 
                    placeholder="Teknik sorunuzu veya merak ettiğiniz konuyu yazın..."
                    autocomplete="off"
                >
                <button id="sendButton" class="send-button">📤</button>
            </div>
            <div class="controls">
                <button id="resetButton" class="control-button">🔄 Yeni Konuşma</button>
                <button id="statusButton" class="control-button">ℹ️ Durum</button>
            </div>
        </div>
    </div>
    
    <script>
        let isLoading = false;
        
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const resetButton = document.getElementById('resetButton');
        const statusButton = document.getElementById('statusButton');
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        resetButton.addEventListener('click', resetConversation);
        statusButton.addEventListener('click', showStatus);
        
        messageInput.focus();
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isLoading) return;
            
            addMessage('user', message);
            messageInput.value = '';
            setLoading(true);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addMessage('bot', data.response, data.category);
                } else {
                    addMessage('bot', 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.');
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage('bot', 'Bağlantı hatası. Lütfen tekrar deneyin.');
            } finally {
                setLoading(false);
            }
        }
        
        function addMessage(sender, text, category = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = sender === 'user' ? '👤' : '🤖';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.textContent = text;
            
            if (category && category !== 'general') {
                const badge = document.createElement('div');
                badge.className = 'category-badge';
                badge.textContent = `📂 ${category}`;
                content.appendChild(badge);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function setLoading(loading) {
            isLoading = loading;
            sendButton.disabled = loading;
            messageInput.disabled = loading;
            
            if (loading) {
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message bot-message';
                loadingDiv.id = 'loading-message';
                
                const avatar = document.createElement('div');
                avatar.className = 'avatar';
                avatar.textContent = '🤖';
                
                const content = document.createElement('div');
                content.className = 'message-content loading';
                content.innerHTML = '<div class="spinner"></div> Fine-tuned model düşünüyor...';
                
                loadingDiv.appendChild(avatar);
                loadingDiv.appendChild(content);
                messagesContainer.appendChild(loadingDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) loadingMessage.remove();
                messageInput.focus();
            }
        }
        
        async function resetConversation() {
            if (!confirm('Konuşmayı sıfırlamak istediğinizden emin misiniz?')) return;
            
            try {
                await fetch('/reset', { method: 'POST' });
                location.reload();
            } catch (error) {
                alert('Sıfırlama hatası');
            }
        }
        
        async function showStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                alert(`Sistem Durumu:\\n\\nModel: ${data.model}\\nKonuşma Uzunluğu: ${data.conversation_length}\\nAPI Key: ${data.api_key_set ? 'Ayarlanmış' : 'Eksik'}`);
            } catch (error) {
                alert('Durum bilgisi alınamadı');
            }
        }
    </script>
</body>
</html>
    """)

@app.post("/chat")
async def chat(request: ChatRequest):
    """Sohbet endpoint'i"""
    try:
        ai = get_simple_ai()
        result = ai.generate_response(request.message)
        return result
    except Exception as e:
        return {
            "response": "Teknik bir sorun yaşıyorum. Lütfen tekrar deneyin.",
            "error": str(e),
            "success": False
        }

@app.post("/reset")
async def reset():
    """Konuşmayı sıfırla"""
    try:
        ai = get_simple_ai()
        ai.reset_conversation()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/status")
async def status():
    """Sistem durumu"""
    try:
        ai = get_simple_ai()
        return ai.get_status()
    except Exception as e:
        return {"error": str(e)}

@app.post("/tts")
async def tts(request: TTSRequest):
    """Text-to-Speech (opsiyonel)"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=request.voice,
            input=request.text[:400]
        )
        
        return Response(
            content=response.content,
            media_type="audio/mpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "system": "ESİT Technical Support AI - Fine-tuned",
        "api_key_set": bool(os.getenv("OPENAI_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
