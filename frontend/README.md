# Frontend

## Setup

From `frontend/`:

```bash
npm install
npm run dev
```

Node ver used is v25.6.0.

## Environment variables

Environment variables should live in `frontend/.env`. IMPORTANT TO NOTE: Git ignores `.env` so you need to recreate it locally. Restart the dev server after editing it since Vite only reads `.env` when the dev server starts.

`VITE_API_URL=https://landmark-classification.onrender.com` holds the backend URL. Important to note that there should not be any trailing slashes.

## Scripts

- `dev` starts a local dev server running at `http://localhost:5173`
- `build` compiles the app into plain HTML, JS, and CSS into `dist/`. `dist/` is what gets deployed.
- `preview` serves the built `dist/` folder locally for testing. Be sure to run `build` first.
- `lint` (runs `oxlint`) checks the code without running it, finding likely errors. 

## Project structure

`src/` holds the frontend app logic.

- `src/App.jsx` is the file that holds the state and calls the backend (`/health` and `/predict`).
- `src/Predictions.jsx` draws the results.
- `src/index.css` is the stylesheet.

## Deploying to Vercel

Set `frontend/` as the root directory.

Make sure to set `VITE_API_URL` as an environment variable in Vercel.

Additionally, Vercel rebuilts the site on every update to main.

`VITE_API_URL` has to be set before the build.

## Troubleshooting
Adblockers can block calls to the backend, be sure to turn them off or browse incognito if possible. I had to disable Brave shields on my end during testing.

