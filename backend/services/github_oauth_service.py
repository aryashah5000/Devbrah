"""
GitHub OAuth Service
"""

import os
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from dotenv import load_dotenv

load_dotenv()

class GitHubOAuthService:
    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:5173/auth/github/callback")
        
        # GitHub OAuth endpoints
        self.authorize_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.api_base = "https://api.github.com"
    
    def is_configured(self) -> bool:
        """Check if GitHub OAuth is configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: str) -> str:
        """Get GitHub OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET")
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email repo read:user",
            "state": state,
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorize_url}?{query_string}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        if not self.is_configured():
            raise ValueError("GitHub OAuth not configured")
        
        async with AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret
        ) as client:
            try:
                token = await client.fetch_token(
                    self.token_url,
                    code=code,
                    redirect_uri=self.redirect_uri
                )
                return token.get("access_token")
            except Exception as e:
                raise ValueError(f"Token exchange failed: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get GitHub user info using access token"""
        import httpx
        
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_resp = await client.get(f"{self.api_base}/user", headers=headers)
            user_data = user_resp.json()
            
            # Get user emails
            emails_resp = await client.get(f"{self.api_base}/user/emails", headers=headers)
            emails_data = emails_resp.json()
            primary_email = next((e["email"] for e in emails_data if e.get("primary")), emails_data[0]["email"] if emails_data else None)
            
            return {
                "id": str(user_data.get("id")),
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "email": primary_email,
                "avatar_url": user_data.get("avatar_url"),
                "bio": user_data.get("bio"),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "access_token": access_token
            }

