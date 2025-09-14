# ZenFlow Mobile-style Frontend

React + Tailwind mobile-style UI. Includes a Form Corrector page that uploads a video to a separate FastAPI service in `form-corrector/`.

## Install & Run (Windows PowerShell)

```powershell
cd .\frontend
npm install
npm start
```

This uses Create React App + Tailwind. The app opens at http://localhost:3000.

## Form Corrector Feature
Start the FastAPI service separately:

```powershell
cd ..\form-corrector
# optional venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt fastapi uvicorn
uvicorn app:app --port 9000 --reload
```

Then open the app and go to Settings → "Open Form Corrector" to upload a short video. The processed MP4 will be displayed and can be downloaded.

If your FastAPI service runs on a different host/port, set an env var before starting:

```powershell
$env:REACT_APP_FORM_CORRECTOR_URL = "http://localhost:9000"; npm start
```

# ZenFlow Mobile-Style Web App (React + Tailwind)

This is a Create React App–compatible project that renders a mobile-style UI similar to the provided screenshots. It uses Tailwind CSS for styling and React Router for navigation.

## Quick start (Windows PowerShell)

1. Install dependencies

```powershell
cd frontend
npm install
```

2. Start the dev server

```powershell
npm start
```

That will open http://localhost:3000/ and show the app inside a centered mobile shell.

## Tech
- React 18, react-router-dom v6
- CRA (react-scripts) build system
- Tailwind CSS 3 (configured via `postcss.config.js` and `tailwind.config.js`)

## Notes
- The bottom tab bar is fixed. On small screens it behaves like a native tab bar.
- All images are placeholders from Unsplash.
- The Form Corrector and Live Coach pages talk to the FastAPI at `REACT_APP_FORM_CORRECTOR_URL` (defaults to `http://localhost:9000`).

## Troubleshooting uploads
- Make sure the FastAPI server is running and shows `GET /health 200`.
- If you see an error like "Unexpected JSON response", check the FastAPI logs for details.
- Try a small MP4/WebM (≤ 20–30s). Large files can take longer and may time out in dev mode.
- On Windows, ensure your PowerShell isn't blocking long-running Python processes.

## Scripts
- `npm start` – Dev server
- `npm run build` – Production build
- `npm test` – CRA test runner