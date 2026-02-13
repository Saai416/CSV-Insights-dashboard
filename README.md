# CSV Insights Dashboard

A production-ready, AI-powered data analysis tool built with Flask and Groq's LLM API.

![Dashboard Preview](https://via.placeholder.com/800x400?text=CSV+Insights+Dashboard+Preview)

## 🚀 Key Features

- **Instant Data Analysis**: Upload any CSV file to get immediate insights.
- **AI-Powered Insights**: Uses Groq's Llama 3.3 70B model to generate summary, trends, outliers, risks, and recommendations.
- **Interactive Visualization**: Auto-generates Bar Charts and Histograms for numeric data.
- **Smart Data Handling**: Robust parsing for various encodings, empty files, and malformed data.
- **Report Management**: Save, view history, and export reports to text files.
- **Contextual Q&A**: Persistent analysis log with history-aware follow-up questions.
- **Production Grade**: Structured error handling, input validation, and secure file processing.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy (SQLite)
- **AI/LLM**: Groq API (Llama-3.3-70b-versatile)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS
- **Visualization**: Chart.js
- **Data Processing**: Pandas

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd csv-insights-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```ini
   GROQ_API_KEY=your_groq_api_key_here
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) in your browser.

## 🧪 Testing

Comprehensive edge case handling is implemented. Test files are provided in the root directory:

- `test_empty.csv`: Verifies empty file rejection.
- `test_headers_only.csv`: Verifies no-data handling.
- `test_duplicates.csv`: Tests duplicate column detection.
- `test_malformed.csv`: Tests parser error handling.

## 🛡️ Security & Robustness

- **Input Validation**: Strict file type and content checks.
- **Error Handling**: User-friendly messages, no stack traces exposed.
- **Data Safety**: Secure filename handling and temporary file cleanup.
- **API Resilience**: Timeouts and error catching for LLM integration.

## 🚀 Deployment Guide
 
This application is ready for deployment on **Render** (easiest, free) or via **Docker**.
 
### Option 1: Deploy to Render (Recommended)
1. Fork/Push this repository to your GitHub.
2. Sign up at [render.com](https://render.com).
3. Click **New +** -> **Web Service**.
4. Connect your repository.
5. Use these settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add Environment Variable:
   - Key: `GROQ_API_KEY`
   - Value: `your_actual_api_key`
7. Click **Create Web Service**.
 
### Option 2: Run with Docker (Fallback)
If hosting is not possible, you can run the app with a single command:
 
```bash
docker-compose up --build
```
The app will be available at `http://localhost:5000`.
 
## 📄 License
 
MIT License - feel free to use and modify.
