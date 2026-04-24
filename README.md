# GrndworkOS — AI Backend (Railway)

## What this is
A small Python server that handles all AI routing for GrndworkOS.
Keeps your API keys off the frontend where anyone could steal them.

## Setup on Railway

### 1. Create a Railway account
Go to https://railway.app and sign up with GitHub.

### 2. Deploy this folder
- Click "New Project" → "Deploy from GitHub repo"
- Push this folder to a GitHub repo first, then connect it
- OR use Railway CLI: `railway init` then `railway up`

### 3. Set environment variables
In Railway dashboard → your project → Variables, add:

| Key         | Value                        |
|-------------|------------------------------|
| CLAUDE_KEY  | your Anthropic API key       |
| GEMINI_KEY  | your Google AI Studio key    |

Never put real keys in this file — always use Railway environment variables.

### 4. Get your Railway URL
After deployment Railway gives you a URL like:
`https://grndworkos-ai-production.up.railway.app`

### 5. Update your frontend
In index.html, find this line at the top of the script:
```
const RAILWAY_URL = 'YOUR_RAILWAY_URL_HERE';
```
Replace with your actual Railway URL.

Then redeploy index.html to Netlify.

## API Endpoints

### GET /health
Check the server is running.
Response: `{ "status": "ok", "service": "grndworkos-ai" }`

### POST /ai
Run an AI action.
Request body: `{ "action": "Generate daily report" }`
Response: `{ "reply": "...", "model": "gemini", "model_label": "Gemini Flash" }`

## How routing works
- Gemini Flash  → simple tasks (reports, summaries, status)
- Claude Haiku  → moderate tasks (dispatch, payroll, scheduling)
- Claude Sonnet → premium tasks (reconciliation, bids, compliance)
