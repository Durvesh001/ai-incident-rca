# AI Incident RCA Assistant

The app uses Gemini to write an RCA narrative from incidents and runbooks selected by the backend. It retains deterministic evidence and confidence scoring, and falls back to the rule-based RCA if Gemini is unavailable.

## Setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).

2. Configure it locally. Do not commit the resulting `backend/.env` file.

   ```powershell
   cd backend
   Copy-Item .env.example .env
   notepad .env
   ```

3. Set `GEMINI_API_KEY` in `backend/.env`, then install and start the backend:

   ```powershell
   py -m venv ../.venv
   ../.venv/Scripts/pip.exe install -r requirements.txt
   ../.venv/Scripts/uvicorn.exe app.main:app --reload
   ```

4. In a second terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Open `http://localhost:3000` and submit an incident.

## Configuration

The default model is `gemini-3.5-flash`. To choose another eligible model, set `GEMINI_MODEL` in `backend/.env`.

The Gemini free tier has model-specific rate limits. Do not send real production secrets or customer data on the free tier.
