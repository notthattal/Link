# Deployment Guide

## Backend (Flask) on Railway

### Prerequisites

- Dockerfile that runs `server.py`
- GitHub repo connected to Railway
- AWS credentials and other secrets available

### Steps

1. Create Railway Project
   - Go to Railway
   - Create a new project and link your GitHub repo
   - Ensure your `Dockerfile` points to `server.py` and exposes port 8080

2. Set Environment Variables (Add the following in Railway > Variables):
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION
    - SPOTIFY_CLIENT_ID
    - SPOTIFY_CLIENT_SECRET
    - GMAIL_CLIENT_ID
    - GMAIL_CLIENT_SECRET

3. Deploy
    - Push to GitHub to trigger deployment
    - Monitor logs for success or errors

## Frontend on Vercel

### Prerequisites

- Frontend repo hosted on GitHub
- Vite project using `import.meta.env`

### Steps

1. Connect Vercel to GitHub
- Import the repo
- Let it auto-detect Vite

2. Set Environment Variables (Go to Vercel > Settings > Environment Variables and add):
    - VITE_SPOTIFY_CLIENT_ID
    - VITE_GMAIL_CLIENT_ID
    - VITE_BACKEND_URL (Railway URL)
    - VITE_COGNITO_DOMAIN
    - VITE_COGNITO_USER_POOL_ID
    - VITE_COGNITO_USER_POOL_CLIENT_ID

3. Redeploy
    - Redeploy from Vercel dashboard or push to GitHub