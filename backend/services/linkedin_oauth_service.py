"""
LinkedIn OAuth Service
Note: LinkedIn OAuth requires approval for most scopes. For hackathon, we'll use a simplified approach.
"""

import os
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from dotenv import load_dotenv

load_dotenv()

class LinkedInOAuthService:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:5173/auth/linkedin/callback")
        
        # LinkedIn OAuth endpoints
        self.authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
    
    def is_configured(self) -> bool:
        """Check if LinkedIn OAuth is configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: str) -> str:
        """Get LinkedIn OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("LinkedIn OAuth not configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET")
        
        from urllib.parse import urlencode
        
        # Use OpenID Connect scopes (LinkedIn deprecated r_liteprofile in 2023)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,  # Will be URL-encoded by urlencode
            "state": state,
            "scope": "openid profile email"  # OpenID Connect scopes
        }
        
        query_string = urlencode(params)
        return f"{self.authorize_url}?{query_string}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        if not self.is_configured():
            raise ValueError("LinkedIn OAuth not configured")
        
        import httpx
        
        # LinkedIn OpenID Connect token request
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=token_data,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    raise ValueError(f"Token exchange failed: {response.status_code} - {error_text}")
                
                token_response = response.json()
                access_token = token_response.get("access_token")
                
                if not access_token:
                    raise ValueError(f"No access token in response: {token_response}")
                
                return access_token
            except httpx.HTTPError as e:
                raise ValueError(f"HTTP error during token exchange: {str(e)}")
            except Exception as e:
                raise ValueError(f"Token exchange failed: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn user info using access token"""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Try OpenID Connect userinfo endpoint first
                userinfo_resp = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers=headers
                )
                
                if userinfo_resp.status_code == 200:
                    userinfo_data = userinfo_resp.json()
                    return {
                        "id": userinfo_data.get("sub", ""),
                        "first_name": userinfo_data.get("given_name", ""),
                        "last_name": userinfo_data.get("family_name", ""),
                        "name": userinfo_data.get("name", ""),
                        "email": userinfo_data.get("email", ""),
                        "picture": userinfo_data.get("picture", ""),
                        "access_token": access_token,
                        "profile_url": f"https://www.linkedin.com/in/{userinfo_data.get('sub', '')}"
                    }
            except Exception as e:
                print(f"⚠️ OpenID Connect failed, trying legacy API: {e}")
            
            # Fallback to legacy API (may not work without Partner Program)
            try:
                profile_resp = await client.get(
                    f"{self.api_base}/me",
                    headers=headers,
                    params={"projection": "(id,firstName,lastName)"}
                )
                
                email_resp = await client.get(
                    f"{self.api_base}/emailAddress?q=members&projection=(elements*(handle~))",
                    headers=headers
                )
                
                profile_data = profile_resp.json() if profile_resp.status_code == 200 else {}
                email_data = email_resp.json() if email_resp.status_code == 200 else {}
                
                first_name = profile_data.get("firstName", {}).get("localized", {}).get("en_US", "")
                last_name = profile_data.get("lastName", {}).get("localized", {}).get("en_US", "")
                email = email_data.get("elements", [{}])[0].get("handle~", {}).get("emailAddress", "") if email_data.get("elements") else ""
                
                return {
                    "id": profile_data.get("id", ""),
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": f"{first_name} {last_name}".strip() or "LinkedIn User",
                    "email": email,
                    "access_token": access_token,
                    "profile_url": f"https://www.linkedin.com/in/{profile_data.get('id', '')}"
                }
            except Exception as e:
                raise ValueError(f"Failed to fetch LinkedIn user info: {str(e)}")

