"""
OAuth Service for Google Authentication
"""

import os
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from dotenv import load_dotenv

load_dotenv()

class OAuthService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/auth/callback")
        self.server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
        
        # Google OAuth endpoints
        self.authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def is_configured(self) -> bool:
        """Check if OAuth is configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: str) -> str:
        """Get Google OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorize_url}?{query_string}"
    
    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for user info"""
        if not self.is_configured():
            raise ValueError("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        
        # Create OAuth client - use context manager for proper lifecycle
        async with AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        ) as client:
            try:
                # Exchange code for token
                token = await client.fetch_token(
                    self.token_url,
                    code=code,
                    redirect_uri=self.redirect_uri
                )
            except Exception as e:
                error_msg = str(e)
                if "redirect_uri_mismatch" in error_msg.lower():
                    raise ValueError(f"Redirect URI mismatch. Expected: {self.redirect_uri}. Make sure it matches Google Cloud Console exactly.")
                elif "invalid_grant" in error_msg.lower():
                    raise ValueError("Invalid authorization code. The code may have expired or been used already.")
                elif "invalid_client" in error_msg.lower():
                    raise ValueError("Invalid client credentials. Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
                else:
                    raise ValueError(f"Token exchange failed: {error_msg}")
            
            # Get user info using the token
            try:
                # Use the token to make authenticated request
                headers = {"Authorization": f"Bearer {token.get('access_token')}"}
                resp = await client.get(self.userinfo_url, headers=headers)
                if resp.status_code != 200:
                    raise ValueError(f"Failed to get user info: {resp.status_code} - {resp.text}")
                user_info = resp.json()
            except Exception as e:
                raise ValueError(f"Failed to fetch user info: {str(e)}")
        
        if not user_info.get("email"):
            raise ValueError("No email returned from Google OAuth")
        
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "provider": "google",
            "provider_id": user_info.get("id"),
            "access_token": token.get("access_token")
        }

