# AI Incident RCA Assistant

This project uses local Ollama for AI-written RCAs. No API key, cloud account, or paid service is required.

## Run on another laptop

1. Install [Ollama](https://ollama.com/download) and download the model:

   ```powershell
   ollama run llama3.2
   ```

   After the model responds once, press `Ctrl+C`. Ollama continues serving its local API at `http://localhost:11434`.

2. Start the backend:

   ```powershell
   cd backend
   py -m venv ../.venv
   ../.venv/Scripts/pip.exe install -r requirements.txt
   ../.venv/Scripts/uvicorn.exe app.main:app --reload
   ```

3. In a second terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

4. Open `http://localhost:3000` and submit an incident.

The backend first selects relevant incidents and runbooks, then sends only those selected records to the local model. If Ollama is stopped or returns an invalid response, the existing rule-based RCA is returned instead.

## Optional configuration

The default model is `llama3.2` at `http://localhost:11434`. Override either setting before starting the backend:

```powershell
$env:OLLAMA_MODEL = "your-local-model"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```
