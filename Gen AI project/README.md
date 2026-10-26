# 💸 Money Mentor AI

Money Mentor is an AI-powered personal expense tracker that transforms casual text into organized financial data. Using a local Ollama model and FastAPI, it allows users to log expenses naturally, track budgets, and receive AI-driven financial health reports.

## 🚀 Features
- **Natural Language Logging**: Type "Spent 200 on snacks" and the AI handles the rest.
- **Budget Tracking**: Visual progress bars for spending limits per category.
- **AI Financial Analyst**: Get a monthly health score and practical saving tips from an AI expert.
- **FastAPI Backend**: Robust and fast asynchronous API.
- **SQLite Database**: Local, lightweight data storage with SQLAlchemy.

## 🛠️ Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: FastAPI, Python 3.10+
- **AI**: LangChain, local Ollama (`qwen2.5:1.5b`)
- **Database**: SQLite, SQLAlchemy
- **DevOps**: GitHub Actions (CI/CD)

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/santhus3j/Fast-API-implementation.git
   cd "Fast-API-implementation/Gen AI project"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Ollama**:
   Install Ollama, then download the model:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
   Keep Ollama running while using the app. No Gemini API key or `.env` file is required.

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the app**:
   Open `http://127.0.0.1:8000/static/index.html` in your browser.

## 📈 CI/CD Pipeline
The project uses GitHub Actions for continuous integration. On every push to the `main` branch, the pipeline:
- Sets up a Python environment.
- Installs dependencies.
- Runs static analysis/linting (if configured).
- Ensures the app builds correctly.

## 📄 License
MIT License
