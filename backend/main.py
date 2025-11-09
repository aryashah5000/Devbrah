"""
devbrah - FastAPI Backend
Microsoft for Startups Hackathon Project
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from models.schemas import (
    UserCreate, UserLogin, UserResponse, NewsletterRequest, NewsletterResponse,
    GitHubConnect, LinkedInConnect, CareerGoal, SkillAnalysis, LearningMode
)
from services.azure_openai import AzureOpenAIService
from services.github_service import GitHubService
from services.linkedin_service import LinkedInService
from services.newsletter_service import NewsletterService
from services.oauth_service import OAuthService
from services.github_oauth_service import GitHubOAuthService
from services.linkedin_oauth_service import LinkedInOAuthService
from database import init_db, get_user_by_email, create_user, get_user_by_oauth, create_oauth_user, AsyncSessionLocal, User

load_dotenv()

# Initialize services
azure_openai = AzureOpenAIService()
github_service = GitHubService()
linkedin_service = LinkedInService()
newsletter_service = NewsletterService(azure_openai)
oauth_service = OAuthService()
github_oauth_service = GitHubOAuthService()
linkedin_oauth_service = LinkedInOAuthService()

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Devbrah API",
    description="Personalized AI Career Growth Newsletter - Microsoft for Startups Track",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Devbrah API",
        "version": "1.0.0",
        "track": "Microsoft for Startups"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "azure_openai_configured": azure_openai.is_configured(),
        "oauth_configured": oauth_service.is_configured()
    }

@app.get("/api/auth/google/authorize")
async def google_authorize():
    """Get Google OAuth authorization URL"""
    import secrets
    state = secrets.token_urlsafe(32)
    auth_url = oauth_service.get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}

@app.get("/api/auth/google/callback")
async def google_callback(code: str, error: str = None):
    """Handle Google OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error from Google: {error}")
    
    try:
        user_info = await oauth_service.get_user_info(code)
        
        # Create or get user
        user = await get_user_by_oauth("google", user_info["provider_id"])
        if not user:
            user = await create_oauth_user(
                email=user_info["email"],
                name=user_info["name"],
                provider="google",
                provider_id=user_info["provider_id"],
                picture_url=user_info.get("picture")
            )
        
        return {
            "access_token": "demo-token",  # In production, generate JWT
            "user": UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                created_at=user["created_at"]
            )
        }
    except ValueError as e:
        # Configuration errors
        print(f"❌ OAuth Configuration Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth not configured: {str(e)}")
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ OAuth Error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

@app.get("/api/auth/github/authorize")
async def github_authorize():
    """Get GitHub OAuth authorization URL"""
    import secrets
    state = secrets.token_urlsafe(32)
    auth_url = github_oauth_service.get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}

@app.get("/api/auth/github/callback")
async def github_callback(code: str, error: str = None, email: str = None):
    """Handle GitHub OAuth callback and store token"""
    if error:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {error}")
    
    try:
        access_token = await github_oauth_service.get_access_token(code)
        user_info = await github_oauth_service.get_user_info(access_token)
        
        # Store GitHub token in user's database record
        if email:
            from sqlalchemy import select
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.email == email))
                user_obj = result.scalar_one_or_none()
                if user_obj:
                    user_obj.github_token = access_token
                    user_obj.github_username = user_info.get("username")
                    await session.commit()
        
        return {
            "connected": True,
            "username": user_info.get("username"),
            "user_info": user_info,
            "token_stored": email is not None
        }
    except Exception as e:
        import traceback
        print(f"❌ GitHub OAuth Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {str(e)}")

@app.get("/api/auth/linkedin/authorize")
async def linkedin_authorize():
    """Get LinkedIn OAuth authorization URL"""
    import secrets
    state = secrets.token_urlsafe(32)
    auth_url = linkedin_oauth_service.get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}

@app.get("/api/auth/linkedin/callback")
async def linkedin_callback(code: str, error: str = None, email: str = None, state: str = None):
    """Handle LinkedIn OAuth callback and store token"""
    if error:
        raise HTTPException(status_code=400, detail=f"LinkedIn OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    try:
        access_token = await linkedin_oauth_service.get_access_token(code)
        user_info = await linkedin_oauth_service.get_user_info(access_token)
        
        # Store LinkedIn token in user's database record
        if email:
            from sqlalchemy import select
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.email == email))
                user_obj = result.scalar_one_or_none()
                if user_obj:
                    user_obj.linkedin_token = access_token
                    user_obj.linkedin_url = user_info.get("profile_url", "")
                    await session.commit()
        
        return {
            "connected": True,
            "name": user_info.get("name"),
            "user_info": user_info,
            "token_stored": email is not None
        }
    except ValueError as e:
        error_msg = str(e)
        # Check if it's a code reuse error (authorization codes can only be used once)
        if "code verifier" in error_msg or "authorization code expired" in error_msg or "does not match" in error_msg:
            print(f"⚠️ LinkedIn OAuth: Code already used or expired. This is normal if callback was called multiple times.")
            # Return success anyway if we have a stored token
            if email:
                user = await get_user_by_email(email)
                if user and user.get("linkedin_token"):
                    return {
                        "connected": True,
                        "name": user.get("linkedin_url", "").split("/")[-1] if user.get("linkedin_url") else "LinkedIn User",
                        "token_stored": True,
                        "message": "Already connected"
                    }
        import traceback
        print(f"❌ LinkedIn OAuth Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"LinkedIn OAuth error: {error_msg}")
    except Exception as e:
        import traceback
        print(f"❌ LinkedIn OAuth Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"LinkedIn OAuth error: {str(e)}")

@app.post("/api/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = await create_user(user_data)
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/users/login")
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        from passlib.context import CryptContext
        
        user = await get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user has a password (not OAuth-only user)
        if not user.get("password_hash"):
            raise HTTPException(
                status_code=401, 
                detail="This account was created with OAuth. Please use Google login instead."
            )
        
        # Verify password
        import hashlib
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception:
            # Fallback if bcrypt has issues
            pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        
        # Handle password verification (account for potential SHA256 pre-hashing)
        password_to_check = user_data.password
        password_bytes = password_to_check.encode('utf-8')
        if len(password_bytes) > 72:
            password_hash = hashlib.sha256(password_bytes).hexdigest()
            password_to_check = password_hash[:72]
        
        try:
            if not pwd_context.verify(password_to_check, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
        except Exception as verify_error:
            # Try with pbkdf2_sha256 if bcrypt verification fails
            print(f"⚠️ Bcrypt verification failed, trying pbkdf2_sha256: {verify_error}")
            pwd_context_fallback = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
            if not pwd_context_fallback.verify(user_data.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return {
            "access_token": "demo-token",  # Simplified for hackathon
            "user": UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                created_at=user["created_at"]
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Login error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/integrations/github", status_code=status.HTTP_200_OK)
async def connect_github(connection: GitHubConnect):
    """Connect GitHub account (mock for hackathon)"""
    # In production, this would use OAuth
    github_data = await github_service.fetch_user_data(connection.username)
    return {
        "connected": True,
        "username": connection.username,
        "repositories": len(github_data.get("repositories", [])),
        "data": github_data
    }

@app.post("/api/integrations/linkedin", status_code=status.HTTP_200_OK)
async def connect_linkedin(connection: LinkedInConnect):
    """Connect LinkedIn account (mock for hackathon)"""
    # In production, this would use OAuth
    linkedin_data = await linkedin_service.fetch_user_data(connection.profile_url)
    return {
        "connected": True,
        "profile_url": connection.profile_url,
        "skills": len(linkedin_data.get("skills", [])),
        "data": linkedin_data
    }

@app.post("/api/analysis/skills", response_model=SkillAnalysis)
async def analyze_skills(
    github_username: str = None,
    linkedin_url: str = None,
    career_goal: CareerGoal = None
):
    """Analyze user skills based on GitHub and LinkedIn data"""
    github_data = None
    linkedin_data = None
    
    if github_username:
        github_data = await github_service.fetch_user_data(github_username)
    
    if linkedin_url:
        linkedin_data = await linkedin_service.fetch_user_data(linkedin_url)
    
    analysis = await azure_openai.analyze_skills(
        github_data=github_data,
        linkedin_data=linkedin_data,
        career_goal=career_goal
    )
    
    return analysis

@app.post("/api/newsletter/generate", response_model=NewsletterResponse)
async def generate_newsletter(request: NewsletterRequest):
    """Generate personalized weekly newsletter and send via email"""
    try:
        # Get user from database to get stored tokens
        user = await get_user_by_email(request.user_email)
        
        # Fetch real GitHub data if user has GitHub token
        github_data = None
        if user and user.get("github_token"):
            try:
                github_data = await github_service.fetch_user_data(user["github_token"])
                print(f"✅ Fetched GitHub data: {len(github_data.get('repositories', []))} repos")
            except Exception as e:
                print(f"⚠️ Failed to fetch GitHub data: {e}")
        elif request.github_username:
            # Fallback: try to use provided username/token
            try:
                github_data = await github_service.fetch_user_data(request.github_username)
            except Exception as e:
                print(f"⚠️ Failed to fetch GitHub data with username: {e}")
        
        # Fetch real LinkedIn data if user has LinkedIn token
        linkedin_data = None
        if user and user.get("linkedin_token"):
            try:
                linkedin_data = await linkedin_service.fetch_user_data(user["linkedin_token"])
                print(f"✅ Fetched LinkedIn data")
            except Exception as e:
                print(f"⚠️ Failed to fetch LinkedIn data: {e}")
        elif request.linkedin_url:
            # Fallback: try to use provided URL/token
            try:
                linkedin_data = await linkedin_service.fetch_user_data(request.linkedin_url)
            except Exception as e:
                print(f"⚠️ Failed to fetch LinkedIn data with URL: {e}")
        
        # Check if we have at least some data
        if not github_data and not linkedin_data:
            raise HTTPException(
                status_code=400, 
                detail="No data available. Please connect at least one account (GitHub or LinkedIn) to generate a newsletter."
            )
        
        # Use the email from the database (OAuth email)
        if user:
            actual_email = user["email"]
            actual_name = user["name"] or request.user_name
        else:
            actual_email = request.user_email
            actual_name = request.user_name
        
        # Generate newsletter with real data analysis
        newsletter = await newsletter_service.generate_newsletter(
            user_email=actual_email,
            user_name=actual_name,
            github_data=github_data,
            linkedin_data=linkedin_data,
            career_goal=request.career_goal,
            learning_mode=request.learning_mode,
            send_email=request.send_email
        )
        
        return newsletter
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Newsletter generation error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate newsletter: {str(e)}. Please check your Azure OpenAI configuration and ensure at least one account is connected."
        )

@app.get("/api/newsletter/preview/{newsletter_id}")
async def preview_newsletter(newsletter_id: str):
    """Preview a generated newsletter"""
    # For hackathon, return a sample newsletter
    return await newsletter_service.get_preview(newsletter_id)

@app.post("/api/subscription/subscribe")
async def subscribe_user(email: str = Query(..., description="User email address")):
    """Subscribe user to newsletter"""
    
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update subscription status
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user_obj = result.scalar_one_or_none()
        if user_obj:
            user_obj.is_subscribed = "true"
            await session.commit()
            await session.refresh(user_obj)
    
    return {"subscribed": True, "message": "Successfully subscribed to newsletter"}

@app.post("/api/subscription/unsubscribe")
async def unsubscribe_user(email: str = Query(..., description="User email address")):
    """Unsubscribe user from newsletter"""
    
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update subscription status
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user_obj = result.scalar_one_or_none()
        if user_obj:
            user_obj.is_subscribed = "false"
            await session.commit()
            await session.refresh(user_obj)
    
    return {"subscribed": False, "message": "Successfully unsubscribed from newsletter"}

@app.get("/api/subscription/status")
async def get_subscription_status(email: str = Query(..., description="User email address")):
    """Get user subscription status"""
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle both string and boolean formats
    is_subscribed = user.get("is_subscribed", False)
    if isinstance(is_subscribed, str):
        is_subscribed = is_subscribed.lower() == "true"
    
    return {"subscribed": is_subscribed}

@app.get("/api/integrations/status")
async def get_integrations_status(email: str = Query(..., description="User email address")):
    """Get user's GitHub and LinkedIn connection status"""
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get LinkedIn name - try to fetch from API if token exists, otherwise extract from URL
    linkedin_name = None
    if user.get("linkedin_token"):
        try:
            # Try to get fresh name from LinkedIn API
            linkedin_data = await linkedin_service.fetch_user_data(user.get("linkedin_token"))
            if linkedin_data and linkedin_data.get("name"):
                linkedin_name = linkedin_data.get("name")
        except Exception as e:
            print(f"⚠️ Could not fetch LinkedIn name from API: {e}")
        
        # Fallback: extract from URL if API call failed
        if not linkedin_name:
            linkedin_url = user.get("linkedin_url", "")
            if linkedin_url and linkedin_url != "https://www.linkedin.com/in/":
                # Extract username from URL like "https://www.linkedin.com/in/username"
                parts = [p for p in linkedin_url.split("/") if p]  # Remove empty parts
                if len(parts) > 0:
                    linkedin_name = parts[-1] if parts[-1] else "LinkedIn User"
            else:
                linkedin_name = "LinkedIn User"
    
    return {
        "github": {
            "connected": bool(user.get("github_token")),
            "username": user.get("github_username") or None
        },
        "linkedin": {
            "connected": bool(user.get("linkedin_token")),
            "name": linkedin_name
        }
    }

@app.post("/api/newsletter/send-weekly")
async def send_weekly_newsletter(email: str = Query(..., description="User email address")):
    """Send weekly newsletter to subscribed user"""
    
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check subscription status - handle both string and boolean
    is_subscribed = user.get("is_subscribed", False)
    if isinstance(is_subscribed, str):
        is_subscribed = is_subscribed.lower() == "true"
    
    if not is_subscribed:
        raise HTTPException(status_code=400, detail="User is not subscribed. Please subscribe first.")
    
    # Generate and send newsletter
    newsletter = await newsletter_service.generate_newsletter(
        user_email=user["email"],
        user_name=user["name"] or "Developer",
        github_data=None,
        linkedin_data=None,
        career_goal=None,
        learning_mode=LearningMode.CAREER_ADVANCEMENT,
        send_email=True
    )
    
    return {"sent": True, "newsletter_id": newsletter.newsletter_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



