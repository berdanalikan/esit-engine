"""
ESİT Technical Support AI - Web Application
FastAPI tabanlı teknik destek web uygulaması
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from tech_support_ai import get_tech_support_ai

# Initialize FastAPI app
app = FastAPI(
    title="ESİT Technical Support AI",
    description="PDF tabanlı akıllı teknik destek sistemi",
    version="1.0.0"
)

# Startup event for feedback system
@app.on_event("startup")
async def startup_event():
    """Initialize feedback system on startup"""
    feedback_logger.info("🚀 ESİT Technical Support AI starting up...")
    feedback_logger.info(f"📊 Loaded feedback system with {len(feedback_data)} existing entries")
    
    if len(feedback_data) > 0:
        total = len(feedback_data)
        positive = sum(1 for f in feedback_data if f["feedback_type"] == "positive")
        negative = sum(1 for f in feedback_data if f["feedback_type"] == "negative")
        satisfaction = (positive / total * 100) if total > 0 else 0
        feedback_logger.info(f"📈 Historical Stats: {positive}👍 {negative}👎 ({satisfaction:.1f}% satisfaction)")
    
    feedback_logger.info("✅ Feedback system ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    feedback_logger.info("🛑 ESİT Technical Support AI shutting down...")
    if save_feedback_data(feedback_data):
        feedback_logger.info("💾 Final feedback data saved successfully")
    else:
        feedback_logger.error("❌ Failed to save final feedback data")
    feedback_logger.info("👋 Shutdown complete")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str

class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"

class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str  # "positive" or "negative"
    user_message: str
    bot_response: str
    timestamp: str
    reason: Optional[str] = None  # Negative feedback reason

# Feedback storage
import json
import logging
from datetime import datetime

# Setup logging for feedback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('feedback.log'),
        logging.StreamHandler()
    ]
)
feedback_logger = logging.getLogger('feedback_system')

# PDF path
PDF_PATH = str(Path.cwd() / "Esit_ECI_User_Manual_Automatic_ENG_v1_7 kopyası.pdf")

# Validate PDF exists at startup
if not Path(PDF_PATH).exists():
    feedback_logger.warning(f"⚠️ PDF file not found at: {PDF_PATH}")
    feedback_logger.info(f"📁 Current working directory: {Path.cwd()}")
    feedback_logger.info(f"📁 Available PDF files: {list(Path.cwd().glob('*.pdf'))}")
else:
    feedback_logger.info(f"✅ PDF file found: {PDF_PATH}")

# Feedback data file path (allow override via FEEDBACK_DIR for deployments)
FEEDBACK_FILE = Path(os.getenv("FEEDBACK_DIR", str(Path(__file__).parent))) / "feedback_data.json"

# Supabase config (if provided, we will store/query feedback there)
# TODO: Replace with your actual Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key-here")

def supabase_enabled() -> bool:
    # Check if credentials are properly set (not placeholder values)
    url_valid = (SUPABASE_URL and 
                 SUPABASE_URL != "https://your-project.supabase.co" and 
                 SUPABASE_URL.startswith("https://") and 
                 ".supabase.co" in SUPABASE_URL)
    key_valid = (SUPABASE_ANON_KEY and 
                 SUPABASE_ANON_KEY != "your-anon-key-here" and 
                 len(SUPABASE_ANON_KEY) > 100)  # JWT tokens are long
    
    return bool(url_valid and key_valid)

def supabase_headers() -> dict:
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }

def supabase_insert_feedback(entry: dict) -> dict:
    url = f"{SUPABASE_URL}/rest/v1/feedback"
    resp = requests.post(url, headers=supabase_headers(), json=entry, params={"select": "*"}, timeout=15)
    if resp.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"Supabase insert failed: {resp.text}")
    return resp.json() if resp.text else {}

def supabase_fetch_feedback(select: str = "*", query: dict | None = None) -> list:
    url = f"{SUPABASE_URL}/rest/v1/feedback"
    params = {"select": select}
    if query:
        params.update(query)
    resp = requests.get(url, headers=supabase_headers(), params=params, timeout=20)
    if resp.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"Supabase fetch failed: {resp.text}")
    return resp.json() if resp.text else []

# Load existing feedback data
def load_feedback_data():
    """Load feedback data from file"""
    try:
        if FEEDBACK_FILE.exists():
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                feedback_logger.info(f"✅ Loaded {len(data)} existing feedback entries")
                return data
        else:
            feedback_logger.info("📝 No existing feedback file found, starting fresh")
            return []
    except Exception as e:
        feedback_logger.error(f"❌ Error loading feedback data: {e}")
        return []

# Save feedback data to file
def save_feedback_data(data):
    """Save feedback data to a single JSON file (no backups)."""
    try:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        feedback_logger.info(f"💾 Saved {len(data)} feedback entries to {FEEDBACK_FILE.name}")
        return True
    except Exception as e:
        feedback_logger.error(f"❌ Error saving feedback data: {e}")
        return False

# Initialize feedback data
feedback_data = load_feedback_data()

# Debug Supabase configuration at startup
feedback_logger.info(f"🔧 STARTUP DEBUG:")
feedback_logger.info(f"   SUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "   SUPABASE_URL: None")
feedback_logger.info(f"   SUPABASE_ANON_KEY length: {len(SUPABASE_ANON_KEY) if SUPABASE_ANON_KEY else 0}")
feedback_logger.info(f"   Supabase enabled: {supabase_enabled()}")

@app.get("/")
async def root():
    """Ana sayfa - ESİT Teknik Destek Arayüzü"""
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#0d1117">
    <title>ESİT Teknik Servis Destek</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0d1117;
            color: #e6edf3;
            height: 100vh;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            -webkit-tap-highlight-color: transparent;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            -khtml-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        
        /* Allow text selection for messages and input */
        .message-content, .message-input, .feedback-additional-input {
            -webkit-user-select: text;
            -khtml-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
            user-select: text;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
        }
        
        /* Hamburger Menu Button */
        .hamburger-btn {
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 1002;
            width: 44px;
            height: 44px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #e6edf3;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .hamburger-btn.hidden {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }
        
        .hamburger-icon {
            font-size: 1rem;
            line-height: 1;
            transition: all 0.2s ease;
        }
        
        .hamburger-btn:hover {
            background: #30363d;
            border-color: #484f58;
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            top: 0;
            left: -280px;
            width: 280px;
            height: 100vh;
            background: #161b22;
            border-right: 1px solid #30363d;
            display: flex;
            flex-direction: column;
            z-index: 1001;
            transition: left 0.3s ease;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .sidebar.open {
            left: 0;
        }
        
        /* Backdrop */
        .sidebar-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: transparent;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .sidebar-backdrop.show {
            opacity: 1;
            visibility: visible;
        }
        
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #30363d;
        }
        
        
        .new-chat-btn {
            width: 100%;
            padding: 10px 14px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #e6edf3;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .new-chat-btn:hover {
            background: #30363d;
            border-color: #484f58;
        }
        
        .sidebar-nav {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
        }
        
        .menu-section {
            margin-bottom: 8px;
        }
        
        .menu-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            font-size: 0.85rem;
            color: #e6edf3;
            font-weight: 500;
            border: 1px solid transparent;
        }
        
        .menu-header:hover {
            background: #21262d;
            border-color: #30363d;
        }
        
        .menu-header.active {
            background: #1f6feb;
            color: white;
        }
        
        .menu-toggle {
            font-size: 0.8rem;
            transition: transform 0.2s ease;
            color: #7d8590;
        }
        
        .menu-toggle.expanded {
            transform: rotate(90deg);
            color: #e6edf3;
        }
        
        .menu-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out, padding 0.3s ease-out;
            padding: 0 12px;
        }
        
        .menu-content.expanded {
            max-height: 300px;
            padding: 8px 12px;
        }
        
        .menu-item {
            padding: 8px 12px;
            margin: 2px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.8rem;
            color: #7d8590;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border-left: 2px solid transparent;
        }
        
        .menu-item:hover {
            background: #21262d;
            color: #e6edf3;
            border-left-color: #1f6feb;
        }
        
        .menu-item.active {
            background: #21262d;
            color: #e6edf3;
            border-left-color: #1f6feb;
        }
        
        .menu-icon {
            display: inline-block;
            width: 16px;
            margin-right: 8px;
            text-align: center;
            font-size: 0.7rem;
        }
        
        
        /* Main Content */
        .main-content {
            width: 100%;
            display: flex;
            flex-direction: column;
            transition: margin-left 0.3s ease;
        }
        
        .header {
            padding: 16px 24px 16px 80px;
            border-bottom: 1px solid #30363d;
            background: #0d1117;
            position: sticky;
            top: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 100;
            backdrop-filter: blur(8px);
            background: rgba(13, 17, 23, 0.95);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header-logo {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .header-logo img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .header-title {
            display: flex;
            flex-direction: column;
        }
        
        .header-title h1 {
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
            color: #e6edf3;
        }
        
        .header-title p {
            color: #7d8590;
            font-size: 0.8rem;
            margin: 0;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #e6edf3;
            font-size: 0.85rem;
        }
        
        .user-avatar {
            width: 28px;
            height: 28px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
        }
        
        /* Chat Area */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0d1117;
        }
        
        .messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: justify-content 0.6s ease-out;
            scroll-behavior: smooth;
            max-height: calc(100vh - 140px);
        }
        
        .messages.chat-started {
            justify-content: flex-start;
            align-items: stretch;
            gap: 16px;
        }

        /* Sidebar: show only first menu-section (Chat History) */
        .sidebar-nav .menu-section { display: none; }
        .sidebar-nav .menu-section:first-child { display: block; }
        
        .messages::-webkit-scrollbar {
            width: 6px;
        }
        
        .messages::-webkit-scrollbar-track {
            background: #161b22;
        }
        
        .messages::-webkit-scrollbar-thumb {
            background: #30363d;
            border-radius: 3px;
        }
        
        .messages::-webkit-scrollbar-thumb:hover {
            background: #484f58;
        }
        
        .welcome-container {
            max-width: 600px;
            text-align: center;
            transition: all 0.6s ease-out;
            transform: translateY(0);
            opacity: 1;
        }
        
        .welcome-container.fade-out {
            opacity: 0;
            transform: translateY(-30px);
            pointer-events: none;
        }
        
        .welcome-container.hidden {
            display: none;
        }
        
        .esit-logo {
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            transition: transform 0.6s ease-out;
        }
        
        .welcome-container.fade-out .esit-logo {
            transform: scale(0.8) rotate(5deg);
        }
        
        .esit-logo img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .welcome-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #e6edf3;
            transition: all 0.6s ease-out;
        }
        
        .welcome-container.fade-out .welcome-title {
            transform: translateX(-20px);
            opacity: 0;
        }
        
        .welcome-subtitle {
            color: #7d8590;
            margin-bottom: 24px;
            font-size: 0.9rem;
            transition: all 0.6s ease-out 0.1s;
        }
        
        .welcome-container.fade-out .welcome-subtitle {
            transform: translateX(20px);
            opacity: 0;
        }
        
        
        .message {
            display: flex;
            gap: 12px;
            max-width: 80%;
            animation: fadeIn 0.3s ease-in;
            margin-bottom: 16px;
            align-items: flex-start;
        }
        
        .user-message {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .bot-message {
            align-self: flex-start;
        }
        
        .feedback-buttons {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            align-items: center;
            align-self: flex-start;
        }
        
        .feedback-btn {
            background: transparent;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 6px 12px;
            color: #7d8590;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .feedback-btn:hover {
            background: #21262d;
            border-color: #484f58;
            color: #e6edf3;
        }
        
        .feedback-btn.positive {
            color: #238636;
            border-color: #238636;
        }
        
        .feedback-btn.negative {
            color: #da3633;
            border-color: #da3633;
        }
        
        .feedback-btn.selected {
            background: rgba(31, 111, 235, 0.1);
            border-color: #1f6feb;
            color: #1f6feb;
        }
        
        .feedback-btn.selected.positive {
            background: rgba(35, 134, 54, 0.1);
            border-color: #238636;
            color: #238636;
        }
        
        .feedback-btn.selected.negative {
            background: rgba(218, 54, 51, 0.1);
            border-color: #da3633;
            color: #da3633;
        }
        
        .feedback-text {
            font-size: 11px;
            color: #7d8590;
            margin-left: 8px;
        }
        
        .feedback-hint {
            font-size: 11px;
            color: #7d8590;
            margin-left: 8px;
            opacity: 0.9;
        }
        
        .feedback-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(13, 17, 23, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            backdrop-filter: blur(4px);
        }
        
        .feedback-modal.show {
            display: flex;
        }
        
        .feedback-modal-content {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
        }
        
        .feedback-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .feedback-modal-title {
            font-size: 18px;
            font-weight: bold;
            color: #e6edf3;
        }
        
        .feedback-modal-close {
            background: transparent;
            border: none;
            color: #7d8590;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .feedback-modal-close:hover {
            background: #21262d;
            color: #e6edf3;
        }
        
        .feedback-modal-body {
            margin-bottom: 20px;
        }
        
        .feedback-modal-label {
            display: block;
            margin-bottom: 8px;
            color: #e6edf3;
            font-weight: 500;
        }
        
        .feedback-reason-options {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
        }
        
        .feedback-reason-option {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .feedback-reason-option:hover {
            background: #21262d;
        }
        
        .feedback-reason-option input[type="radio"] {
            margin: 0;
        }
        
        .feedback-reason-option label {
            cursor: pointer;
            color: #e6edf3;
            margin: 0;
        }
        
        .feedback-additional-input {
            width: 100%;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
            color: #e6edf3;
            font-size: 14px;
            resize: vertical;
            min-height: 80px;
        }
        
        .feedback-additional-input:focus {
            outline: none;
            border-color: #1f6feb;
            box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.1);
        }
        
        .feedback-modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }
        
        .feedback-modal-btn {
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        
        .feedback-modal-btn.cancel {
            background: transparent;
            border-color: #30363d;
            color: #e6edf3;
        }
        
        .feedback-modal-btn.cancel:hover {
            background: #21262d;
        }
        
        .feedback-modal-btn.submit {
            background: #da3633;
            color: white;
        }
        
        .feedback-modal-btn.submit:hover {
            background: #c93936;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            flex-shrink: 0;
        }
        
        .user-message .avatar {
            background: #1f6feb;
            color: white;
        }
        
        .bot-message .avatar {
            background: #21262d;
            border: 1px solid #30363d;
            color: #e6edf3;
        }
        
        .message-content {
            background: #161b22;
            border: 1px solid #30363d;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
            color: #e6edf3;
        }
        
        .user-message .message-content {
            background: #1f6feb;
            border-color: #1f6feb;
            color: white;
        }
        
        /* Input Area */
        .input-area {
            padding: 16px 24px;
            border-top: 1px solid #30363d;
            background: rgba(13, 17, 23, 0.95);
            backdrop-filter: blur(8px);
            position: sticky;
            bottom: 0;
            z-index: 50;
        }
        
        .input-note {
            text-align: center;
            font-size: 0.75rem;
            color: #7d8590;
            margin-bottom: 12px;
        }
        
        .input-container {
            display: flex;
            gap: 8px;
            align-items: flex-end;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .tts-button {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            background: #21262d;
            color: #7d8590;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            border: 1px solid #30363d;
        }
        
        .tts-button:hover {
            background: #30363d;
            border-color: #484f58;
            color: #e6edf3;
        }
        
        .tts-button.active {
            background: #1f6feb;
            border-color: #1f6feb;
            color: white;
        }
        
        .message-input {
            flex: 1;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 20px;
            padding: 10px 16px;
            color: #e6edf3;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
            resize: none;
            min-height: 40px;
            max-height: 120px;
        }
        
        .message-input:focus {
            border-color: #1f6feb;
        }
        
        .message-input::placeholder {
            color: #7d8590;
        }
        
        .send-button {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            background: #21262d;
            color: #7d8590;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .send-button:hover:not(:disabled) {
            background: #30363d;
            color: #e6edf3;
        }
        
        .send-button:disabled {
            background: #21262d;
            color: #484f58;
            cursor: not-allowed;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #7d8590;
        }
        
        .spinner {
            width: 14px;
            height: 14px;
            border: 2px solid #30363d;
            border-top: 2px solid #1f6feb;
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
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                max-width: 320px;
                left: -100%;
            }
            
            .sidebar.open {
                left: 0;
            }
            
            .main-content {
                margin-left: 0;
                padding: 0 4px;
            }
            
            .hamburger-btn {
                display: flex;
                top: 12px;
                left: 12px;
                width: 36px;
                height: 36px;
                font-size: 18px;
            }
            
            .header {
                padding: 12px 16px 12px 60px;
                min-height: 60px;
            }
            
            .header-left {
                align-items: center;
                gap: 8px;
            }
            
            .header-logo {
                width: 24px;
                height: 24px;
            }
            
            .header-title {
                font-size: 14px;
                line-height: 1.2;
            }
            
            .user-info {
                position: absolute;
                right: 16px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 11px;
            }
            
            .messages {
                padding: 8px;
                max-height: calc(100vh - 180px);
            }
            
            .message {
                margin-bottom: 12px;
                max-width: 100%;
            }
            
            .message-content {
                max-width: 85%;
                padding: 10px 12px;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .avatar {
                width: 28px;
                height: 28px;
                font-size: 12px;
            }
            
            .feedback-buttons {
                margin-top: 6px;
                gap: 6px;
                flex-wrap: wrap;
            }
            
            .feedback-btn {
                padding: 4px 8px;
                font-size: 11px;
                gap: 3px;
                flex: 0 0 auto;
            }
            
            .feedback-text {
                font-size: 10px;
            }
            
            .input-area {
                padding: 8px 12px 12px;
            }
            
            .input-note {
                font-size: 11px;
                margin-bottom: 8px;
            }
            
            .input-container {
                gap: 6px;
            }
            
            .message-input {
                font-size: 14px;
                padding: 10px 12px;
                min-height: 44px;
            }
            
            .send-button, .tts-button {
                width: 36px;
                height: 36px;
                font-size: 16px;
                min-width: 36px;
            }
            
            .welcome-container {
                padding: 16px;
                margin: 16px 8px;
            }
            
            .esit-logo {
                width: 48px;
                height: 48px;
                margin-bottom: 12px;
            }
            
            .welcome-title {
                font-size: 18px;
                margin-bottom: 8px;
            }
            
            .welcome-subtitle {
                font-size: 14px;
                line-height: 1.3;
            }
            
            /* Mobile Feedback Modal */
            .feedback-modal-content {
                width: 95%;
                max-width: none;
                margin: 8px;
                padding: 16px;
                border-radius: 8px;
                max-height: 85vh;
            }
            
            .feedback-modal-title {
                font-size: 16px;
            }
            
            .feedback-modal-close {
                width: 28px;
                height: 28px;
                font-size: 20px;
            }
            
            .feedback-reason-option {
                padding: 12px 8px;
                margin: 2px 0;
            }
            
            .feedback-reason-option label {
                font-size: 14px;
            }
            
            .feedback-additional-input {
                min-height: 60px;
                font-size: 14px;
                padding: 10px;
            }
            
            .feedback-modal-footer {
                gap: 8px;
                margin-top: 16px;
            }
            
            .feedback-modal-btn {
                padding: 10px 16px;
                font-size: 14px;
                flex: 1;
                text-align: center;
            }
        }
        
        /* Small Mobile (iPhone SE, etc.) */
        @media (max-width: 480px) {
            .header {
                padding: 8px 12px 8px 50px;
                min-height: 50px;
            }
            
            .hamburger-btn {
                width: 32px;
                height: 32px;
                top: 9px;
                left: 9px;
                font-size: 16px;
            }
            
            .header-logo {
                width: 20px;
                height: 20px;
            }
            
            .header-title {
                font-size: 12px;
            }
            
            .user-info {
                font-size: 10px;
                right: 12px;
            }
            
            .messages {
                padding: 6px;
                max-height: calc(100vh - 160px);
            }
            
            .message-content {
                max-width: 90%;
                padding: 8px 10px;
                font-size: 13px;
            }
            
            .avatar {
                width: 24px;
                height: 24px;
                font-size: 10px;
            }
            
            .input-area {
                padding: 6px 8px 8px;
            }
            
            .message-input {
                font-size: 13px;
                padding: 8px 10px;
                min-height: 40px;
            }
            
            .send-button, .tts-button {
                width: 32px;
                height: 32px;
                font-size: 14px;
                min-width: 32px;
            }
            
            .feedback-btn {
                padding: 3px 6px;
                font-size: 10px;
                gap: 2px;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Hamburger Menu Button -->
        <button class="hamburger-btn" id="hamburgerBtn" onclick="toggleSidebar()">
            <span class="hamburger-icon" id="hamburgerIcon">☰</span>
        </button>
        
        <!-- Sidebar Backdrop -->
        <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeSidebar()"></div>
        
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <button class="new-chat-btn" onclick="resetConversation()">
                    <span>+</span> Yeni sohbet
                </button>
            </div>
            
            <div class="sidebar-nav">
                <!-- Sohbet Geçmişi -->
                <div class="menu-section">
                    <div class="menu-header" onclick="toggleMenu('chatHistory')">
                        <span><span class="menu-icon">💬</span>Sohbet Geçmişi</span>
                        <span class="menu-toggle" id="chatHistoryToggle">▶</span>
                    </div>
                    <div class="menu-content" id="chatHistoryContent">
                        <div class="menu-item">📋 ECI cihazı kalibrasyonu</div>
                        <div class="menu-item">⚠️ Load cell bağlantı sorunu</div>
                        <div class="menu-item">⚙️ Menü 2.5 erişim problemi</div>
                        <div class="menu-item">🔧 Bakım ve temizlik</div>
                        <div class="menu-item">📊 Ağırlık ölçüm hatası</div>
                    </div>
                </div>

                <!-- Teknik Destek -->
                <div class="menu-section">
                    <div class="menu-header" onclick="toggleMenu('support')">
                        <span><span class="menu-icon">🛠️</span>Teknik Destek</span>
                        <span class="menu-toggle" id="supportToggle">▶</span>
                    </div>
                    <div class="menu-content" id="supportContent">
                        <div class="menu-item active">📞 Genel destek</div>
                        <div class="menu-item">⚖️ Kalibrasyon adımları</div>
                        <div class="menu-item">📱 Ağırlık göstergesi</div>
                        <div class="menu-item">🔌 Bağlantı sorunları</div>
                        <div class="menu-item">🖥️ Ekran problemleri</div>
                    </div>
                </div>

                <!-- Ürün Kategorileri -->
                <div class="menu-section">
                    <div class="menu-header" onclick="toggleMenu('products')">
                        <span><span class="menu-icon">📦</span>Ürün Kategorileri</span>
                        <span class="menu-toggle" id="productsToggle">▶</span>
                    </div>
                    <div class="menu-content" id="productsContent">
                        <div class="menu-item">🎨 ART Serisi</div>
                        <div class="menu-item">🧠 SMART Serisi</div>
                        <div class="menu-item">⚡ ECI Serisi</div>
                        <div class="menu-item">📏 Ölçüm Cihazları</div>
                        <div class="menu-item">🔩 Yedek Parçalar</div>
                    </div>
                </div>

                <!-- Hızlı Erişim -->
                <div class="menu-section">
                    <div class="menu-header" onclick="toggleMenu('quickAccess')">
                        <span><span class="menu-icon">⚡</span>Hızlı Erişim</span>
                        <span class="menu-toggle" id="quickAccessToggle">▶</span>
                    </div>
                    <div class="menu-content" id="quickAccessContent">
                        <div class="menu-item">❓ Sık sorulan sorular</div>
                        <div class="menu-item">🚨 Hata kodları</div>
                        <div class="menu-item">📞 İletişim</div>
                        <div class="menu-item">📖 Kullanım kılavuzu</div>
                        <div class="menu-item">🎥 Video eğitimler</div>
                    </div>
                </div>

                <!-- Ayarlar -->
                <div class="menu-section">
                    <div class="menu-header" onclick="toggleMenu('settings')">
                        <span><span class="menu-icon">⚙️</span>Ayarlar</span>
                        <span class="menu-toggle" id="settingsToggle">▶</span>
                    </div>
                    <div class="menu-content" id="settingsContent">
                        <div class="menu-item">🌙 Tema ayarları</div>
                        <div class="menu-item">🔔 Bildirimler</div>
                        <div class="menu-item">🌍 Dil seçimi</div>
                        <div class="menu-item">📊 Veriler</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="header">
                <div class="header-left">
                    <div class="header-logo">
                        <img src="/logo" alt="ESİT Logo" />
                    </div>
                    <div class="header-title">
                        <h1>Teknik Servis Destek</h1>
                        <p>Yapay Zeka Asistanı</p>
                    </div>
                </div>
                <div class="user-info">
                    <div class="user-avatar">👤</div>
                    <span>Oturum</span>
                </div>
            </div>
            
            <div class="chat-container">
                <div id="messages" class="messages">
                    <div class="welcome-container">
                        <div class="esit-logo">
                            <img src="/logo" alt="ESİT Logo" />
                        </div>
                        <div class="welcome-title">ESİT Teknik Destek Asistanına hoş geldiniz!</div>
                        <div class="welcome-subtitle">Size nasıl yardımcı olabilirim?</div>
            </div>
        </div>
        
                <div class="input-area">
                    <div class="input-note">Asistan hata yapabilir. Önemli bilgileri lütfen kontrol edin.</div>
                    <div class="input-container">
                        <textarea 
                            id="messageInput" 
                            class="message-input" 
                            placeholder="Herhangi bir şey sor"
                            rows="1"
                        ></textarea>
                        <button id="ttsButton" class="tts-button" onclick="toggleTTS()" title="Sesli Yanıt">
                            <span id="ttsIcon">🔊</span>
                        </button>
                        <button id="sendButton" class="send-button">
                            <span>↗</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Feedback Modal -->
    <div id="feedbackModal" class="feedback-modal">
        <div class="feedback-modal-content">
            <div class="feedback-modal-header">
                <h3 class="feedback-modal-title">Geri Bildirim</h3>
                <button class="feedback-modal-close" onclick="closeFeedbackModal()">×</button>
            </div>
            <div class="feedback-modal-body">
                <label class="feedback-modal-label">Bu cevap neden yararlı olmadı?</label>
                <div class="feedback-reason-options">
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-incorrect" name="feedback-reason" value="Yanlış bilgi verdi">
                        <label for="reason-incorrect">Yanlış bilgi verdi</label>
                    </div>
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-incomplete" name="feedback-reason" value="Eksik açıklama">
                        <label for="reason-incomplete">Eksik açıklama</label>
                    </div>
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-unclear" name="feedback-reason" value="Anlaşılmaz">
                        <label for="reason-unclear">Anlaşılmaz</label>
                    </div>
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-irrelevant" name="feedback-reason" value="Konuyla alakasız">
                        <label for="reason-irrelevant">Konuyla alakasız</label>
                    </div>
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-too-long" name="feedback-reason" value="Çok uzun">
                        <label for="reason-too-long">Çok uzun</label>
                    </div>
                    <div class="feedback-reason-option">
                        <input type="radio" id="reason-other" name="feedback-reason" value="Diğer">
                        <label for="reason-other">Diğer</label>
                    </div>
                </div>
                <label class="feedback-modal-label">Ek açıklama (isteğe bağlı):</label>
                <textarea id="feedbackAdditionalText" class="feedback-additional-input" placeholder="Nasıl iyileştirebileceğimizi belirtebilirsiniz..."></textarea>
            </div>
            <div class="feedback-modal-footer">
                <button class="feedback-modal-btn cancel" onclick="closeFeedbackModal()">İptal</button>
                <button class="feedback-modal-btn submit" onclick="submitNegativeFeedback()">Gönder</button>
            </div>
        </div>
    </div>
    
    <script>
        let isLoading = false;
        let selectedCategory = 'ECI';
        let ttsEnabled = false;
        
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const ttsButton = document.getElementById('ttsButton');
        const ttsIcon = document.getElementById('ttsIcon');
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        messageInput.focus();
        
        function selectCategory(category) {
            selectedCategory = category;
        }
        
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
        
        // Click anywhere outside sidebar to close
        document.addEventListener('click', function(e) {
            const sidebar = document.getElementById('sidebar');
            const hamburgerBtn = document.getElementById('hamburgerBtn');
            
            // If sidebar is open and click is outside sidebar and not on hamburger button
            if (sidebar.classList.contains('open') && 
                !sidebar.contains(e.target) && 
                !hamburgerBtn.contains(e.target)) {
                closeSidebar();
            }
        });
        
        function openSidebar() {
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('sidebarBackdrop');
            const hamburgerBtn = document.getElementById('hamburgerBtn');
            
            sidebar.classList.add('open');
            backdrop.classList.add('show');
            hamburgerBtn.classList.add('hidden');
        }
        
        function closeSidebar() {
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('sidebarBackdrop');
            const hamburgerBtn = document.getElementById('hamburgerBtn');
            
            sidebar.classList.remove('open');
            backdrop.classList.remove('show');
            hamburgerBtn.classList.remove('hidden');
        }
        
        // Close sidebar on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSidebar();
            }
        });
        
        // Global variables for feedback modal
        let currentFeedbackMessageId = null;
        let currentFeedbackBotResponse = null;
        
        // Feedback modal functions
        function openFeedbackModal(messageId, botResponse) {
            currentFeedbackMessageId = messageId;
            currentFeedbackBotResponse = botResponse;
            
            // Reset form
            const reasonInputs = document.querySelectorAll('input[name="feedback-reason"]');
            reasonInputs.forEach(input => input.checked = false);
            document.getElementById('feedbackAdditionalText').value = '';
            
            // Show modal
            document.getElementById('feedbackModal').classList.add('show');
        }
        
        function closeFeedbackModal() {
            document.getElementById('feedbackModal').classList.remove('show');
            currentFeedbackMessageId = null;
            currentFeedbackBotResponse = null;
        }
        
        async function submitNegativeFeedback() {
            const selectedReason = document.querySelector('input[name="feedback-reason"]:checked');
            const additionalText = document.getElementById('feedbackAdditionalText').value;
            
            if (!selectedReason) {
                alert('Lütfen bir neden seçin.');
                return;
            }
            
            let reason = selectedReason.value;
            if (additionalText.trim()) {
                reason += ` - ${additionalText.trim()}`;
            }
            
            await submitFeedback(currentFeedbackMessageId, 'negative', currentFeedbackBotResponse, reason);
            closeFeedbackModal();
        }
        
        // Close modal on backdrop click
        document.getElementById('feedbackModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeFeedbackModal();
            }
        });
        
        // Close modal on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.getElementById('feedbackModal').classList.contains('show')) {
                closeFeedbackModal();
            }
        });
        
        // Feedback submission function
        async function submitFeedback(messageId, feedbackType, botResponse, reason = null) {
            try {
                const response = await fetch('/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message_id: messageId,
                        feedback_type: feedbackType,
                        user_message: window.lastUserMessage || '',
                        bot_response: botResponse,
                        timestamp: new Date().toISOString(),
                        reason: reason
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Update button states
                    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
                    if (messageDiv) {
                        const buttons = messageDiv.querySelectorAll('.feedback-btn');
                        buttons.forEach(btn => btn.classList.remove('selected'));
                        
                        const selectedBtn = messageDiv.querySelector(`.feedback-btn.${feedbackType}`);
                        if (selectedBtn) {
                            selectedBtn.classList.add('selected');
                            
                            // Add feedback text
                            let feedbackText = messageDiv.querySelector('.feedback-text');
                            if (!feedbackText) {
                                feedbackText = document.createElement('span');
                                feedbackText.className = 'feedback-text';
                                messageDiv.querySelector('.feedback-buttons').appendChild(feedbackText);
                            }
                            feedbackText.textContent = feedbackType === 'positive' ? 'Teşekkürler!' : 'Geri bildiriminiz alındı';
                        }
                    }
                } else {
                    console.error('Feedback submission failed:', data);
                }
            } catch (error) {
                console.error('Error submitting feedback:', error);
            }
        }
        
        // TTS Functions
        function toggleTTS() {
            // şimdilik devre dışı. görünüm kalsın.
            ttsEnabled = false;
            if (ttsButton) {
                ttsButton.classList.remove('active');
                if (ttsIcon) ttsIcon.textContent = '🔊';
                ttsButton.title = 'Sesli Yanıt (yakında)';
            }
        }
        
        async function playTTS(text) {
            if (!text || text.length > 500) return;
            
            try {
                const response = await fetch('/tts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text.substring(0, 500),
                        voice: 'nova'
                    })
                });
                
                if (response.ok) {
                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    
                    audio.play().catch(console.error);
                    audio.addEventListener('ended', () => {
                        URL.revokeObjectURL(audioUrl);
                    });
                }
            } catch (error) {
                console.error('TTS error:', error);
            }
        }
        
        function toggleMenu(menuId) {
            const content = document.getElementById(menuId + 'Content');
            const toggle = document.getElementById(menuId + 'Toggle');
            const header = toggle.parentElement;
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                toggle.classList.remove('expanded');
                header.classList.remove('active');
            } else {
                content.classList.add('expanded');
                toggle.classList.add('expanded');
                header.classList.add('active');
            }
        }
        
        // Menu item click handler
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.menu-item').forEach(item => {
                item.addEventListener('click', function() {
                    // Remove active class from all items
                    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
                    // Add active class to clicked item
                    this.classList.add('active');
                });
            });
        });
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isLoading) return;
            
            // Animate welcome message fade out on first message
            const welcomeMsg = document.querySelector('.welcome-container');
            const messagesContainer = document.getElementById('messages');
            
            if (welcomeMsg && !welcomeMsg.classList.contains('fade-out')) {
                // Start fade out animation
                welcomeMsg.classList.add('fade-out');
                messagesContainer.classList.add('chat-started');
                
                // Remove welcome message after animation completes
                setTimeout(() => {
                    welcomeMsg.classList.add('hidden');
                }, 600);
            }
            
            addMessage('user', message);
            messageInput.value = '';
            messageInput.style.height = 'auto';
            setLoading(true);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: message
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    addMessage('bot', data.response, messageId);
                    
                    // Store last user message for feedback
                    window.lastUserMessage = message;
                    
                    // Auto TTS if enabled
                    if (false && ttsEnabled && data.response) {
                        playTTS(data.response);
                    }
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
        
        function addMessage(sender, text, messageId = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            if (messageId) messageDiv.dataset.messageId = messageId;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = sender === 'user' ? '👤' : '🤖';
            
            // Wrap content and feedback vertically so buttons sit under bubble
            const contentWrapper = document.createElement('div');
            contentWrapper.style.display = 'flex';
            contentWrapper.style.flexDirection = 'column';
            contentWrapper.style.alignItems = sender === 'user' ? 'flex-end' : 'flex-start';
            contentWrapper.style.maxWidth = '100%';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.textContent = text;
            
            contentWrapper.appendChild(content);
            
            // Add feedback buttons for bot messages under the bubble
            if (sender === 'bot' && messageId) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'feedback-buttons';
                feedbackDiv.style.marginLeft = '2px';
                
                const positiveBtn = document.createElement('button');
                positiveBtn.className = 'feedback-btn positive';
                positiveBtn.innerHTML = '<span>👍</span><span>İyi</span>';
                positiveBtn.onclick = () => submitFeedback(messageId, 'positive', text);
                
                const negativeBtn = document.createElement('button');
                negativeBtn.className = 'feedback-btn negative';
                negativeBtn.innerHTML = '<span>👎</span><span>Kötü</span>';
                negativeBtn.onclick = () => openFeedbackModal(messageId, text);
                
                feedbackDiv.appendChild(positiveBtn);
                feedbackDiv.appendChild(negativeBtn);
                const hint = document.createElement('span');
                hint.className = 'feedback-hint';
                hint.textContent = '(Lütfen cevabı değerlendiriniz.)';
                feedbackDiv.appendChild(hint);
                contentWrapper.appendChild(feedbackDiv);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentWrapper);
            messagesContainer.appendChild(messageDiv);
            
            // Smooth scroll to bottom after a short delay
            setTimeout(() => {
                messagesContainer.scrollTo({
                    top: messagesContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }, 100);
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
                content.innerHTML = '<div class="spinner"></div> Düşünüyorum...';
                
                loadingDiv.appendChild(avatar);
                loadingDiv.appendChild(content);
                messagesContainer.appendChild(loadingDiv);
                
                // Smooth scroll to bottom
                setTimeout(() => {
                    messagesContainer.scrollTo({
                        top: messagesContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                }, 100);
            } else {
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) {
                    loadingMessage.remove();
                }
                messageInput.focus();
            }
        }
        
        async function resetConversation() {
            try {
                await fetch('/reset', { method: 'POST' });
                location.reload();
            } catch (error) {
                alert('Sıfırlama hatası');
            }
        }
        
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat(request: ChatRequest):
    """Ana sohbet endpoint'i"""
    try:
        # Get AI instance
        ai = get_tech_support_ai(PDF_PATH)
        if not ai:
            raise HTTPException(status_code=500, detail="AI system not initialized")
        
        # Generate response
        result = ai.generate_response(request.message)
        
        return result
        
    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "response": "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen tekrar deneyin.",
            "error": str(e),
            "success": False
        }

@app.post("/reset")
async def reset_conversation():
    """Konuşmayı sıfırla"""
    try:
        ai = get_tech_support_ai(PDF_PATH)
        if ai:
            ai.reset_conversation()
        return {"success": True, "message": "Konuşma sıfırlandı"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Text-to-Speech endpoint"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=request.voice,
            input=request.text[:500]  # Limit text length
        )
        
        return Response(
            content=response.content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for bot responses"""
    try:
        # Add feedback to storage
        feedback_entry = {
            "message_id": request.message_id,
            "feedback_type": request.feedback_type,
            "user_message": request.user_message,
            "bot_response": request.bot_response,
            "timestamp": request.timestamp,
            "reason": request.reason,
            "created_at": datetime.now().isoformat(),
            "server_timestamp": datetime.now().isoformat(),
            "user_agent": request.headers.get("user-agent", "unknown") if hasattr(request, 'headers') else "unknown"
        }
        
        # Debug logging
        feedback_logger.info(f"🔍 DEBUG - Feedback submission:")
        feedback_logger.info(f"   Supabase enabled: {supabase_enabled()}")
        feedback_logger.info(f"   SUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "None")
        feedback_logger.info(f"   SUPABASE_ANON_KEY: {'***' + SUPABASE_ANON_KEY[-10:] if SUPABASE_ANON_KEY else 'None'}")
        
        # Prefer Supabase if configured
        if supabase_enabled():
            try:
                result = supabase_insert_feedback(feedback_entry)
                feedback_logger.info(f"✅ Supabase insert successful: {result}")
            except Exception as supabase_error:
                feedback_logger.error(f"❌ Supabase insert failed: {supabase_error}")
                # Fallback to local storage
                feedback_data.append(feedback_entry)
                save_feedback_data(feedback_data)
                feedback_logger.info("📁 Saved to local JSON as fallback")
        else:
            feedback_data.append(feedback_entry)
            save_feedback_data(feedback_data)
            feedback_logger.info("📁 Saved to local JSON (Supabase not enabled)")

        # Log the feedback submission
        feedback_logger.info(f"📝 New feedback received:")
        feedback_logger.info(f"   Type: {request.feedback_type}")
        feedback_logger.info(f"   Message ID: {request.message_id}")
        feedback_logger.info(f"   User Message: {request.user_message[:50]}...")
        feedback_logger.info(f"   Bot Response: {request.bot_response[:50]}...")
        if request.reason:
            feedback_logger.info(f"   Reason: {request.reason}")
        
        # Stats
        
        if supabase_enabled():
            rows = supabase_fetch_feedback(select="feedback_type")
            total = len(rows)
            positive = sum(1 for r in rows if r.get("feedback_type") == "positive")
            negative = sum(1 for r in rows if r.get("feedback_type") == "negative")
        else:
            total = len(feedback_data)
            positive = sum(1 for f in feedback_data if f["feedback_type"] == "positive")
            negative = sum(1 for f in feedback_data if f["feedback_type"] == "negative")
        satisfaction = (positive / total * 100) if total > 0 else 0
        
        feedback_logger.info(f"📊 Current Stats: {positive}👍 {negative}👎 ({satisfaction:.1f}% satisfaction)")
        
        return {"status": "success", "message": "Feedback submitted successfully"}
        
    except Exception as e:
        feedback_logger.error(f"❌ Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/analysis")
async def get_feedback_analysis():
    """Get feedback analysis and suggestions for improvement"""
    try:
        import json
        from collections import Counter
        
        if supabase_enabled():
            rows = supabase_fetch_feedback(select="feedback_type,bot_response")
            total = len(rows)
            positive = sum(1 for r in rows if r.get("feedback_type") == "positive")
            negative = sum(1 for r in rows if r.get("feedback_type") == "negative")
            negative_responses = [ (r.get("bot_response") or "")[:100] for r in rows if r.get("feedback_type") == "negative" ]
        else:
            if not feedback_data:
                return {
                    "total_feedback": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "satisfaction_rate": 0,
                    "suggestions": []
                }
            total = len(feedback_data)
            positive = sum(1 for f in feedback_data if f["feedback_type"] == "positive")
            negative = sum(1 for f in feedback_data if f["feedback_type"] == "negative")
            negative_responses = [f["bot_response"][:100] for f in feedback_data if f["feedback_type"] == "negative"]
        satisfaction_rate = (positive / total * 100) if total > 0 else 0
        
        # Generate improvement suggestions
        suggestions = []
        
        if satisfaction_rate < 70:
            suggestions.append("Overall satisfaction is low. Consider reviewing response quality and accuracy.")
        
        if negative > positive:
            suggestions.append("More negative than positive feedback. Review recent responses for common issues.")
        
        if len(set(negative_responses)) < len(negative_responses) * 0.7:
            suggestions.append("Similar responses getting negative feedback. Consider improving these specific response patterns.")
        
        return {
            "total_feedback": total,
            "positive_count": positive,
            "negative_count": negative,
            "satisfaction_rate": round(satisfaction_rate, 2),
            "suggestions": suggestions,
            "recent_negative_feedback": negative_responses[-5:] if negative_responses else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/daily-report")
async def get_daily_feedback_report():
    """Get daily feedback report for monitoring"""
    try:
        from datetime import datetime, timedelta
        
        # Get today's feedback
        today = datetime.now().date()
        if supabase_enabled():
            start = f"{today.isoformat()}T00:00:00Z"
            # basitçe created_at >= start filtrasyonu, üst sınır olmadan da çoğu durumda yeterli
            rows = supabase_fetch_feedback(select="feedback_type,user_message,bot_response,created_at", query={"created_at": f"gte.{start}"})
            total_today = len(rows)
            positive_today = sum(1 for r in rows if r.get("feedback_type") == "positive")
            negative_today = sum(1 for r in rows if r.get("feedback_type") == "negative")
            recent_negative = [r for r in rows if r.get("feedback_type") == "negative"][-5:]
            overall_rows = supabase_fetch_feedback(select="feedback_type")
            overall_total = len(overall_rows)
            overall_pos = sum(1 for r in overall_rows if r.get("feedback_type") == "positive")
            overall_neg = sum(1 for r in overall_rows if r.get("feedback_type") == "negative")
        else:
            today_feedback = []
            for feedback in feedback_data:
                try:
                    feedback_date = datetime.fromisoformat(feedback.get("created_at", feedback.get("timestamp", ""))).date()
                    if feedback_date == today:
                        today_feedback.append(feedback)
                except:
                    continue
            total_today = len(today_feedback)
            positive_today = sum(1 for f in today_feedback if f["feedback_type"] == "positive")
            negative_today = sum(1 for f in today_feedback if f["feedback_type"] == "negative")
            recent_negative = [f for f in today_feedback if f["feedback_type"] == "negative"][-5:]
            overall_total = len(feedback_data)
            overall_pos = sum(1 for f in feedback_data if f["feedback_type"] == "positive")
            overall_neg = sum(1 for f in feedback_data if f["feedback_type"] == "negative")
        satisfaction_today = (positive_today / total_today * 100) if total_today > 0 else 0
        
        report = {
            "date": today.isoformat(),
            "daily_stats": {
                "total_feedback": total_today,
                "positive_count": positive_today,
                "negative_count": negative_today,
                "satisfaction_rate": round(satisfaction_today, 2)
            },
            "recent_negative_samples": [
                {
                    "user_message": (f.get("user_message") or "")[:100],
                    "bot_response": (f.get("bot_response") or "")[:100],
                    "timestamp": f.get("created_at", f.get("timestamp"))
                }
                for f in recent_negative
            ],
            "overall_stats": {
                "total_all_time": overall_total,
                "positive_all_time": overall_pos,
                "negative_all_time": overall_neg
            }
        }
        
        # Log daily report
        feedback_logger.info(f"📊 Daily Report Generated for {today}")
        feedback_logger.info(f"   Today: {positive_today}👍 {negative_today}👎 ({satisfaction_today:.1f}%)")
        feedback_logger.info(f"   All Time: {len(feedback_data)} total feedback entries")
        
        return report
        
    except Exception as e:
        feedback_logger.error(f"❌ Error generating daily report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logo")
async def get_logo():
    """ESİT logosu"""
    logo_path = Path(__file__).parent / "esit_beyaz kopyası.png"
    if logo_path.exists():
        return FileResponse(str(logo_path), media_type="image/png")
    else:
        # Debug info
        current_dir = Path(__file__).parent
        files = list(current_dir.glob("*.png"))
        raise HTTPException(status_code=404, detail=f"Logo not found. Available PNG files: {[f.name for f in files]}")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "system": "ESİT Technical Support AI",
        "pdf_available": Path(PDF_PATH).exists(),
        "supabase_enabled": supabase_enabled()
    }

@app.get("/test-supabase")
async def test_supabase():
    """Test Supabase connection"""
    try:
        debug_info = {
            "supabase_url": SUPABASE_URL[:50] + "..." if SUPABASE_URL else "None",
            "supabase_key_set": bool(SUPABASE_ANON_KEY),
            "supabase_key_length": len(SUPABASE_ANON_KEY) if SUPABASE_ANON_KEY else 0,
            "supabase_enabled": supabase_enabled()
        }
        
        if not supabase_enabled():
            return {
                "status": "error", 
                "message": "Supabase credentials not configured properly",
                "debug": debug_info
            }
        
        # Test connection by trying to fetch feedback
        result = supabase_fetch_feedback(select="id", query={"limit": "1"})
        return {
            "status": "success", 
            "message": "Supabase connection successful",
            "sample_count": len(result),
            "debug": debug_info
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Supabase connection failed: {str(e)}",
            "debug": debug_info if 'debug_info' in locals() else {}
        }

@app.post("/migrate-feedback-to-supabase")
async def migrate_feedback_to_supabase():
    """Migrate existing local feedback data to Supabase"""
    try:
        if not supabase_enabled():
            return {"status": "error", "message": "Supabase credentials not configured"}
        
        if not feedback_data:
            return {"status": "info", "message": "No local feedback data to migrate"}
        
        migrated_count = 0
        errors = []
        
        for entry in feedback_data:
            try:
                supabase_insert_feedback(entry)
                migrated_count += 1
            except Exception as e:
                errors.append(f"Failed to migrate entry {entry.get('message_id', 'unknown')}: {str(e)}")
        
        return {
            "status": "success" if not errors else "partial_success",
            "message": f"Migrated {migrated_count}/{len(feedback_data)} feedback entries",
            "migrated_count": migrated_count,
            "total_count": len(feedback_data),
            "errors": errors[:5]  # Show first 5 errors
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Migration failed: {str(e)}"}

# For Vercel deployment
def handler(request):
    return app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
