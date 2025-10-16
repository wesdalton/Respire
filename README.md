# Respire

AI-Powered Burnout Prevention Platform integrating WHOOP health data with personalized insights.

**Built by**: Wes Dalton, UPenn '27
**Status**: Production-ready backend, frontend architecture complete

**Try it out**: [tryrespire.ai](https://tryrespire.ai)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (via Supabase)

### Backend Setup
```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
python3 main.py
```
API: http://localhost:8000
Docs: http://localhost:8000/docs

### Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
App: http://localhost:5173

---

## Project Structure

```
Respire/
├── apps/
│   ├── api/              # FastAPI backend
│   └── web/              # React frontend
├── packages/
│   └── database/         # PostgreSQL schema
├── archive/              # Old code (not in use)
└── README.md
```

---

## Features

- **Authentication**: Supabase Auth with JWT
- **WHOOP Integration**: OAuth 2.0, full API v2
- **Health Analytics**: Recovery, HRV, sleep, strain
- **Mood Tracking**: Daily ratings + statistics
- **Burnout Risk Algorithm**: 5-factor analysis
- **AI Insights**: GPT-4 recommendations
- **Dashboard**: Complete health overview

---

## Tech Stack

**Backend**: FastAPI, SQLAlchemy, PostgreSQL, OpenAI  
**Frontend**: React 18, TypeScript, Vite, Tailwind CSS  
**Infrastructure**: Supabase, Railway, Vercel

---

## Project Stats

- **~8,000 lines of code**
- **21 API endpoints**
- **7 database tables**
- **3 weeks development**
- **$5-10/month hosting**

---

Built using FastAPI, React, Supabase, and OpenAI
