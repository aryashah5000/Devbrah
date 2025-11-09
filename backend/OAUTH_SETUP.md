# 🔐 OAuth Setup Guide for GitHub and LinkedIn

## GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: devbrah
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:5173/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and generate a **Client Secret**

### Step 2: Update .env

```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:5173/auth/github/callback
```

## LinkedIn OAuth Setup

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in app details
4. In "Auth" tab, add redirect URL:
   - `http://localhost:5173/auth/linkedin/callback`
5. Request these scopes:
   - `r_liteprofile` (basic profile)
   - `r_emailaddress` (email)
6. Copy **Client ID** and **Client Secret**

### Step 2: Update .env

```env
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:5173/auth/linkedin/callback
```

## Note on LinkedIn API

LinkedIn API v2 has strict requirements:
- Basic profile and email are available with standard OAuth
- Full profile, skills, and experiences require **LinkedIn Partner Program** approval
- For hackathon, we'll use available endpoints and enhance with structure

## Testing

1. Start backend and frontend
2. Login with Google
3. Go to Dashboard
4. Click "Login with GitHub" or "Login with LinkedIn"
5. Authorize the app
6. Generate newsletter - it will analyze your real code and profile!

