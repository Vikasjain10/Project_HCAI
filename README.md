# VitalTrack — HCAI Wellness Monitoring System

**VitalTrack** is an AI-powered personal health monitoring application that analyzes wearable metrics to assess **stress**, **fatigue**, and **overall wellness**. It combines machine learning predictions with explainable AI (SHAP) and optional LLM-generated insights to help users understand their health trends over time.

---

## Features

- **Stress & fatigue prediction** — ML models trained on wearable-derived features
- **Wellness scoring** — composite wellness score with recovery and readiness signals
- **Full health assessment** — single endpoint for stress, fatigue, fatigue type, and wellness
- **Explainable AI** — SHAP-based feature explanations for model transparency
- **AI advisor** — LLM-powered summaries and recommendations (OpenRouter, Gemini, or OpenAI)
- **Session tracking** — compare assessments across sessions and track trends
- **User authentication** — signup/login with JWT and personal profile management
- **Interactive dashboard** — React UI with charts, history, insights, and dark mode

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, FastAPI, Uvicorn, SQLAlchemy, scikit-learn, XGBoost, SHAP |
| **Frontend** | React, Vite, Tailwind CSS, Recharts, Axios |
| **AI / LLM** | OpenRouter (recommended), Google Gemini, OpenAI |
| **Database** | SQLite |
| **Data** | Pandas, wearable JSON/CSV pipeline |

---

## Project Structure

```
HCAI_Project/
├── backend/              # FastAPI API, ML models, auth, explainability
│   ├── api.py            # Main API routes
│   ├── llm_service.py    # LLM integration
│   ├── explain_service.py
│   └── train_*.py        # Model training scripts
├── dashboard/            # React frontend
│   └── src/
│       ├── pages/        # Home, Dashboard, Insights, Profile, etc.
│       └── components/   # Charts, forms, AI insight cards
├── data/
│   └── final_dataset.csv # Processed dataset for ML (included)
├── notebooks/            # EDA and analysis
├── reports/              # Model explanation plots
├── requirements.txt
├── .env.example
└── start.ps1 / start.bat # Quick start scripts
```

> **Note:** Large raw wearable files in `data/raw/` are excluded from the repository due to GitHub size limits. They remain on your local machine for data pipeline scripts.

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- (Optional) API key for LLM features — [OpenRouter](https://openrouter.ai/keys) recommended

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vikasjain10/Project_HCAI.git
cd Project_HCAI
```

### 2. Environment variables

Copy the example env file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
JWT_SECRET=your-secure-secret
```

> Without an LLM API key, the app still works using built-in rule-based recommendations.

### 3. Backend setup

From the project root:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python backend/create_database.py
```

### 4. Frontend setup

```bash
cd dashboard
npm install
cd ..
```

---

## Running the Application

### Option A — Quick start (Windows)

```powershell
.\start.ps1
```

Or double-click `start.bat`.

### Option B — Manual start

**Terminal 1 — Backend API**

```bash
cd backend
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend dashboard**

```bash
cd dashboard
npm run dev
```

### Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| API docs | http://127.0.0.1:8000/docs |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |
| `GET` | `/auth/me` | Get current user profile |
| `GET` | `/dashboard/summary` | Dashboard overview metrics |
| `POST` | `/full_assessment` | Run full stress/fatigue/wellness assessment |
| `POST` | `/explain` | Get SHAP feature explanations |
| `POST` | `/recommendation` | Get AI recommendations |
| `GET` | `/sessions/history` | Session comparison history |
| `GET` | `/history/predictions` | Past prediction records |
| `GET` | `/analytics` | Analytics data for charts |

---

## ML Models

The system includes trained models for:

- **Stress level** — classification from heart rate, sleep, activity, and wellness features
- **Fatigue detection** — binary fatigue prediction
- **Fatigue type** — categorization of fatigue patterns
- **Wellness score** — composite score from recovery, readiness, and physiological signals

Training scripts (run from project root):

```bash
python backend/train_stress.py
python backend/train_fatigue.py
python backend/train_fatigue_type.py
```

---

## LLM Integration

The AI advisor supports multiple providers (priority order):

1. **OpenRouter** (recommended)
2. **Google Gemini**
3. **OpenAI**
4. **Built-in rules** (fallback when no API key is configured)

LLM outputs include: summary, stress/fatigue/wellness explanations, key issues, daily/weekly suggestions, and recommendations.

---

## Author

**Vikas Jain** 

**Sanjana Munikrishnappa**

**Gaurav Tyaagi** 

**Utkarsh Gautam** 

---

## License

This project was developed as part of an HCAI (Human-Centered AI) academic project. Contact the author for usage terms.
