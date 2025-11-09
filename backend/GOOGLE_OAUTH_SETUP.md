# 🔐 Google OAuth Setup Guide

## Setting up Google OAuth for devbrah

This guide will help you set up Google OAuth so users can sign in with their Google account, and newsletters will be sent to their Google email.

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen first:
     - User Type: External
     - App name: devbrah
     - User support email: your email
     - Developer contact: your email
     - Scopes: email, profile, openid
   - Application type: **Web application**
   - Name: devbrah Web Client
   - Authorized JavaScript origins:
     - `http://localhost:5173`
     - `http://localhost:3000`
   - Authorized redirect URIs:
     - `http://localhost:5173/auth/callback`
   - Click "Create"
   - Copy the **Client ID** and **Client Secret**

## Step 2: Update .env File

Add these to your `backend/.env` file:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
SERVER_BASE_URL=http://localhost:8000
```

## Step 3: Test OAuth Flow

1. Start your backend:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Go to http://localhost:5173
4. Click "Continue with Google"
5. Sign in with your Google account
6. You'll be redirected back and logged in
7. Generate a newsletter - it will be sent to your Google email!

## How It Works

1. User clicks "Continue with Google"
2. User is redirected to Google sign-in
3. User authorizes the app
4. Google redirects back with an authorization code
5. Backend exchanges code for user info (email, name, picture)
6. User is created/logged in with their Google email
7. When generating newsletters, the system uses the OAuth email

## Production Deployment

For production, update:
- `GOOGLE_REDIRECT_URI` to your production URL (e.g., `https://devbrah.ai/auth/callback`)
- Add production URLs to Google Cloud Console authorized redirect URIs
- Update `SERVER_BASE_URL` to your production backend URL

## Troubleshooting

- **"redirect_uri_mismatch"**: Make sure the redirect URI in .env matches exactly what's in Google Cloud Console
- **"invalid_client"**: Check that CLIENT_ID and CLIENT_SECRET are correct
- **"access_denied"**: User cancelled the OAuth flow
- **Email not received**: Check that the user's email from OAuth is being used (check backend logs)

## Security Notes

- Never commit `.env` file with real credentials
- Use environment variables in production
- The OAuth flow uses secure HTTPS endpoints
- User emails are stored securely in the database

