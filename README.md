# 🇮🇳 Saarathi-AI

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

> **Your AI-powered guide to discovering government schemes in India**

Saarathi-AI helps Indian citizens navigate the complex landscape of central and state government schemes. Simply fill in your profile, and our intelligent system will match you with schemes you're eligible for, complete with explanations and application guidance.

---

## ✨ Features

- 🎯 **Smart Eligibility Matching** - Get personalized scheme recommendations based on your profile
- 💬 **AI Assistant** - Chat with our AI to understand schemes, eligibility criteria, and application processes
- 🗺️ **Multi-State Coverage** - Supports central schemes and state-specific programs (Karnataka, Delhi, Maharashtra, Tamil Nadu)
- 🔍 **Detailed Scheme Information** - View complete details including benefits, documents required, and official links
- 🎨 **Modern UI** - Beautiful glassmorphism design with dark theme
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- 🔐 **Admin Panel** - Manage schemes and sync data from external sources

---

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing-fast development
- **Tailwind CSS** for styling
- **Lucide React** for icons
- PWA-ready with offline support

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Robust relational database (Neon-hosted)
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Bytez AI** - LLM integration with mock fallback

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL database (or Neon account)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your database URL
echo "DATABASE_URL=postgresql://user:password@host/dbname" > .env

# Run the server
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with DB status |
| GET | `/api/schemes/` | List all schemes |
| POST | `/api/schemes/seed-demo-data` | Seed database with demo schemes |
| POST | `/api/eligibility/check` | Check eligibility for schemes |
| POST | `/api/assistant/chat` | Chat with AI assistant |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |

---

## 🎯 How It Works

1. **Fill Your Profile** - Enter your details: state, age, occupation, income, etc.
2. **Get Matched** - Our eligibility engine analyzes your profile against all available schemes
3. **Explore Schemes** - View eligible schemes with detailed information and reasons
4. **Ask Questions** - Use the AI assistant to get clarifications and guidance
5. **Apply** - Follow the application process with direct links to official portals

---

## 🗂️ Project Structure

```
Saarathi-AI/
├── backend/
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic (eligibility, AI)
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── db.py            # Database configuration
│   └── main.py          # FastAPI app entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── contexts/    # React contexts
│   │   ├── utils/       # Utility functions
│   │   └── types.ts     # TypeScript types
│   └── public/          # Static assets
│
└── README.md
```

---

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://user:password@host/dbname
BYTEZ_API_KEY=your_bytez_api_key_here  # Optional
USE_BYTEZ_LLM=true  # Set to false to use mock AI
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Government scheme data sourced from official portals
- Built with modern web technologies for optimal performance
- Designed to make government schemes accessible to all citizens

---

<div align="center">
  <strong>Made with ❤️ for the people of India</strong>
</div>
