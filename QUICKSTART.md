# Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- Groq API key (get free at https://console.groq.com)

## Installation (5 Minutes)

### 1. Navigate to Project
```bash
cd csv-insights-app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
# Copy template
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux

# Edit .env and add your Groq API key:
# GROQ_API_KEY=gsk-your-actual-key-here
```

### 6. Run Application
```bash
python app.py
```

## Access Points

- **API Root:** http://localhost:5000/
- **Health Check (JSON):** http://localhost:5000/status
- **Health Dashboard (UI):** http://localhost:5000/status/ui

## Quick Test

### Upload a CSV
```bash
curl -F "file=@sample.csv" http://localhost:5000/upload
```

### Check Health
```bash
curl http://localhost:5000/status
```

Or open in browser: http://localhost:5000/status/ui

## Full Documentation

See [README.md](README.md) for:
- Complete API documentation
- 10-scenario test suite
- Troubleshooting guide
- Architecture details
