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
- This app is a UI scaffold; no backend calls are made.

## Scripts
- `npm start` – Dev server
- `npm run build` – Production build
- `npm test` – CRA test runner