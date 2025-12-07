# Saarathi-AI
AI Government Scheme Navigator

## Tech
- Frontend: React + Tailwind + PWA
- Backend: FastAPI + PostgreSQL
- AI: Qwen3 via Bytez + mock fallback

## Running

Backend:
```
cd backend
python -m venv .venv
source .venv/bin/activate (or .venv\Scripts\activate on Windows)
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```