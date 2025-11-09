"""
Pydantic models for devbrah API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LearningMode(str, Enum):
    CAREER_ADVANCEMENT = "career_advancement"
    INTERNSHIP_PATH = "internship_path"
    TECH_REFRESH = "tech_refresh"

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

class GitHubConnect(BaseModel):
    username: str  # Can be username or OAuth token
    token: Optional[str] = None  # OAuth token if available

class LinkedInConnect(BaseModel):
    profile_url: str  # Can be profile URL or OAuth token
    token: Optional[str] = None  # OAuth token if available

class CareerGoal(BaseModel):
    target_role: str
    target_company: Optional[str] = None
    description: Optional[str] = None

class CodeInsight(BaseModel):
    file_path: str
    code_snippet: str
    feedback: str
    suggestion: str
    complexity: Optional[str] = None

class SkillRecommendation(BaseModel):
    skill: str
    current_level: str
    target_level: str
    demand_percentage: Optional[float] = None
    learning_link: str
    priority: int

class CareerReadiness(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    skill_alignment: float = Field(..., ge=0, le=100)
    code_quality_score: float = Field(..., ge=0, le=100)
    missing_skills: List[str]
    strong_skills: List[str]

class SkillAnalysis(BaseModel):
    career_readiness: CareerReadiness
    code_insights: List[CodeInsight]
    skill_recommendations: List[SkillRecommendation]
    analysis_date: datetime

class NewsletterRequest(BaseModel):
    user_email: EmailStr
    user_name: str
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    career_goal: Optional[CareerGoal] = None
    learning_mode: LearningMode = LearningMode.CAREER_ADVANCEMENT
    send_email: bool = True

class NewsletterResponse(BaseModel):
    newsletter_id: str
    user_name: str
    generated_at: datetime
    career_readiness: CareerReadiness
    code_insights: List[CodeInsight]
    skill_recommendations: List[SkillRecommendation]
    learning_links: List[Dict[str, str]]
    html_content: str
    summary: str



