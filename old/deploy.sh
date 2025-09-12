#!/bin/bash

# ESİT Technical Support AI - Deployment Script

echo "🚀 ESİT Technical Support AI Deployment"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo "📦 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Set environment variables in Railway dashboard:"
echo "   - OPENAI_API_KEY"
echo "   - SUPABASE_URL" 
echo "   - SUPABASE_ANON_KEY"
echo ""
echo "2. Add persistent volume for PDF files"
echo ""
echo "3. Test your deployment:"
echo "   railway open"
