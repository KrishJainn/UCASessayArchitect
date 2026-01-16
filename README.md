# InfoYoung India - UCAS Personal Statement Generator

A Streamlit-powered AI application that helps students craft compelling UCAS Personal Statements using the Phoenix AI Engine.

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

### Step 1: Push to GitHub

Make sure these files are in your GitHub repo:
- `app.py` - Main Streamlit application
- `backend.py` - AI generation logic
- `ingest_essays.py` - Essay ingestion module
- `requirements.txt` - Python dependencies
- `logo.png` - InfoYoung India logo
- `.streamlit/config.toml` - Streamlit configuration
- `brain_config.json` - Pre-trained brain configuration (optional)

**DO NOT** push:
- `.env` (contains your API key)
- `venv/` or `__pycache__/`
- `chroma_db/` (will be created at runtime)

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set the main file path to `app.py`
5. Add your secret in **Advanced Settings > Secrets**:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
6. Click **Deploy**

### Step 3: Configure Secrets

In Streamlit Cloud, go to your app settings and add:

```toml
[secrets]
GEMINI_API_KEY = "your_gemini_api_key_here"
```

## 📁 Project Structure

```
├── app.py                 # Main Streamlit app
├── backend.py             # AI generation engine
├── ingest_essays.py       # Essay ingestion logic
├── requirements.txt       # Dependencies
├── logo.png               # InfoYoung India logo
├── brain_config.json      # Learned style rules
├── .streamlit/
│   └── config.toml        # Streamlit theme config
└── pdfs/                  # Upload folder for training essays
```

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key |

## ✨ Features

- **3-Step Wizard**: Academic Profile → Motivation → Generate
- **Phoenix AI Engine**: Uses Gemini 2.5 Flash with 24k thinking tokens
- **CV Upload**: Extract experiences from PDF/DOCX
- **Style Bible**: Learns from exemplar essays
- **Word Export**: Download as formatted .docx

## 📝 License

MIT License - InfoYoung India
