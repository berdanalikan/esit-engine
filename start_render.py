#!/usr/bin/env python3
"""
Render.com için özel başlatma scripti
"""

import os
import sys
from pathlib import Path

# Render'da PORT environment variable'ı otomatik set edilir
PORT = os.getenv("PORT", "8000")

# PDF dosyasının varlığını kontrol et
PDF_PATH = "Esit_ECI_User_Manual_Automatic_ENG_v1_7 kopyası.pdf"
if not Path(PDF_PATH).exists():
    print(f"⚠️ PDF file not found: {PDF_PATH}")
    print("📁 Available files:")
    for f in Path(".").glob("*.pdf"):
        print(f"   - {f.name}")
    print("📁 Available files:")
    for f in Path(".").glob("*"):
        if f.is_file():
            print(f"   - {f.name}")

# Environment variables kontrolü
required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {missing_vars}")
    print("🔧 Please set these in Render dashboard:")
    for var in missing_vars:
        print(f"   - {var}")
    sys.exit(1)

print(f"✅ All environment variables set")
print(f"🚀 Starting server on port {PORT}")

# FastAPI uygulamasını başlat
if __name__ == "__main__":
    import uvicorn
    from app import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(PORT),
        log_level="info",
        access_log=True
    )
