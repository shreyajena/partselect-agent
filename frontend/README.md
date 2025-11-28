

## Local development

The frontend expects the FastAPI backend from `../backend` to be running locally.

1. Start the backend
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Configure the frontend API base URL (optional if using the default `http://localhost:8000`)
   ```bash
   # .env.local
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. Start the frontend
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Tech stack

- Vite + React + TypeScript
- Tailwind CSS + shadcn/ui
- Custom chat widget in `src/components/chat`

## Backend integration

Chat messages are sent to the FastAPI `/chat` endpoint via `src/api/chat.ts`.
To change environments, update `VITE_API_BASE_URL`.
