# AI Gov Scheme Navigator - Frontend

Modern, professional UI built with React, TypeScript, and Tailwind CSS.

## Features

- 🎨 Modern UI inspired by 21st.dev design patterns
- 🌙 Dark theme with gradient backgrounds
- 📱 Fully responsive (mobile & desktop)
- ✨ Smooth animations and transitions
- 🔍 Real-time form validation
- 🎯 Eligibility matching with backend API

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file (optional):
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Configuration

Set the backend API URL in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

Default: `http://localhost:8000/api`

## Project Structure

```
src/
├── components/
│   ├── ProfileCard.tsx      # User profile form
│   ├── SchemesCard.tsx      # Matching schemes display
│   └── SchemeModal.tsx      # Scheme details modal
├── App.tsx                  # Main app component
├── config.ts                # API configuration
├── types.ts                 # TypeScript interfaces
└── index.css                # Tailwind styles
```

## Build

```bash
npm run build
```

Output will be in `dist/` directory.
