"""
Database setup and operations for devbrah
"""

from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./devbrah.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    created_at = Column(DateTime, default=datetime.utcnow)
    github_username = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    career_goal = Column(Text, nullable=True)
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    oauth_provider_id = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    is_subscribed = Column(String, default="false")  # 'true' or 'false' as string
    github_token = Column(Text, nullable=True)  # GitHub OAuth token
    linkedin_token = Column(Text, nullable=True)  # LinkedIn OAuth token

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "password_hash": user.password_hash,  # Include password_hash for login verification
                "created_at": user.created_at,
                "github_username": user.github_username,
                "linkedin_url": user.linkedin_url,
                "oauth_provider": user.oauth_provider,
                "picture_url": user.picture_url,
                "is_subscribed": user.is_subscribed == "true" if user.is_subscribed else False,
                "github_token": user.github_token,
                "linkedin_token": user.linkedin_token
            }
    return None

async def get_user_by_oauth(provider: str, provider_id: str) -> dict:
    """Get user by OAuth provider and ID"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_provider_id == provider_id
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at,
                "github_username": user.github_username,
                "linkedin_url": user.linkedin_url,
                "oauth_provider": user.oauth_provider,
                "picture_url": user.picture_url,
                "is_subscribed": user.is_subscribed == "true" if user.is_subscribed else False,
                "github_token": user.github_token,
                "linkedin_token": user.linkedin_token
            }
    return None

async def create_oauth_user(email: str, name: str, provider: str, provider_id: str, picture_url: Optional[str] = None) -> dict:
    """Create a new user from OAuth"""
    import uuid
    
    async with AsyncSessionLocal() as session:
        # Check if user already exists by email
        existing = await get_user_by_email(email)
        if existing:
            # Update OAuth info if needed
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                user.oauth_provider = provider
                user.oauth_provider_id = provider_id
                user.picture_url = picture_url
                if not user.name:
                    user.name = name
                await session.commit()
                await session.refresh(user)
                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "created_at": user.created_at,
                    "oauth_provider": user.oauth_provider,
                    "picture_url": user.picture_url,
                    "is_subscribed": user.is_subscribed == "true" if user.is_subscribed else False
                }
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            password_hash=None,  # OAuth users don't have passwords
            created_at=datetime.utcnow(),
            oauth_provider=provider,
            oauth_provider_id=provider_id,
            picture_url=picture_url,
            is_subscribed="false"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at,
            "oauth_provider": user.oauth_provider,
            "picture_url": user.picture_url,
            "is_subscribed": user.is_subscribed == "true" if user.is_subscribed else False
        }

async def create_user(user_data) -> dict:
    """Create a new user"""
    import uuid
    from passlib.context import CryptContext
    import hashlib
    
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    except Exception as e:
        # Fallback if bcrypt has issues - use pbkdf2_sha256 instead
        print(f"⚠️ Bcrypt initialization issue, using pbkdf2_sha256: {e}")
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    # Bcrypt has a 72-byte limit, so we'll hash the password first if it's too long
    password = user_data.password
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Hash with SHA256 first, then bcrypt (common workaround)
        password_hash = hashlib.sha256(password_bytes).hexdigest()
        password = password_hash[:72]  # Ensure it's within bcrypt limit
    
    async with AsyncSessionLocal() as session:
        try:
            password_hash = pwd_context.hash(password)
        except Exception as e:
            print(f"⚠️ Password hashing error: {e}, trying alternative method")
            # Fallback to pbkdf2_sha256 if bcrypt fails
            pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
            password_hash = pwd_context.hash(user_data.password)
        
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            is_subscribed="false"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at
        }



