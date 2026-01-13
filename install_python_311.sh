#!/bin/bash

echo "🚀 Starting Python 3.11 Upgrade..."

# 1. Install Python 3.11 via Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first."
    exit 1
fi

echo "📦 Checking/Installing Python 3.11..."
brew install python@3.11

# 2. Find the installed python3.11 binary
PYTHON_BIN="$(brew --prefix)/bin/python3.11"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Python 3.11 installation failed or not found at expected path."
    exit 1
fi
echo "✅ Python 3.11 found at $PYTHON_BIN"

# 3. Clean up old environment
if [ -d "venv" ]; then
    echo "🧹 Removing old virtual environment (python 3.9)..."
    rm -rf venv
fi

# 4. Create new Virtual Environment
echo "✨ Creating new venv with Python 3.11..."
"$PYTHON_BIN" -m venv venv

# 5. Activate and Install Dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Essential packages for the College Essay App
pip install streamlit \
    google-generativeai \
    chromadb \
    langchain-chroma \
    langchain-huggingface \
    langchain-community \
    python-dotenv \
    docx2txt \
    watchdog

echo "----------------------------------------------------"
echo "🎉 SUCCESS! Environment upgraded to Python 3.11."
echo "----------------------------------------------------"
echo "To start the app, run:"
echo "source venv/bin/activate"
echo "streamlit run app.py"
