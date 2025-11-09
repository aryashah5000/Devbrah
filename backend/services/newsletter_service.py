"""
Newsletter Generation Service
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from jinja2 import Template

from models.schemas import (
    NewsletterResponse, CareerReadiness, CodeInsight, SkillRecommendation,
    LearningMode
)
from services.azure_openai import AzureOpenAIService
from services.email_service import EmailService

class NewsletterService:
    def __init__(self, azure_openai: AzureOpenAIService):
        self.azure_openai = azure_openai
        self.email_service = EmailService()
        self.newsletter_template = self._load_template()
    
    async def generate_newsletter(
        self,
        user_email: str,
        user_name: str,
        github_data: Optional[Dict[str, Any]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None,
        career_goal: Optional[Any] = None,
        learning_mode: LearningMode = LearningMode.CAREER_ADVANCEMENT,
        send_email: bool = True
    ) -> NewsletterResponse:
        """Generate personalized newsletter and optionally send via email"""
        
        try:
            # Get skill analysis
            analysis = await self.azure_openai.analyze_skills(
                github_data=github_data,
                linkedin_data=linkedin_data,
                career_goal=career_goal
            )
        except Exception as e:
            print(f"❌ Error in skill analysis: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise with better message
            raise ValueError(f"Failed to analyze skills: {str(e)}. Please check Azure OpenAI configuration or ensure at least one account (GitHub/LinkedIn) is connected.")
        
        # Generate learning links
        learning_links = self._generate_learning_links(analysis.skill_recommendations)
        
        # Generate summary
        summary = self._generate_summary(analysis, learning_mode)
        
        # Use provided name or fallback
        display_name = user_name or linkedin_data.get("name", "Developer") if linkedin_data else "Developer"
        
        # Render HTML newsletter
        html_content = self._render_newsletter(
            user_name=display_name,
            analysis=analysis,
            learning_links=learning_links,
            learning_mode=learning_mode
        )
        
        newsletter_id = str(uuid.uuid4())
        
        # Send email if requested
        email_sent = False
        if send_email:
            subject = f"🚀 Your Devbrah Weekly Newsletter - {datetime.utcnow().strftime('%B %d, %Y')}"
            email_sent = await self.email_service.send_newsletter(
                to_email=user_email,
                to_name=display_name,
                subject=subject,
                html_content=html_content
            )
        
        return NewsletterResponse(
            newsletter_id=newsletter_id,
            user_name=display_name,
            generated_at=datetime.utcnow(),
            career_readiness=analysis.career_readiness,
            code_insights=analysis.code_insights,
            skill_recommendations=analysis.skill_recommendations,
            learning_links=learning_links,
            html_content=html_content,
            summary=summary
        )
    
    def _generate_learning_links(self, recommendations: list[SkillRecommendation]) -> list[Dict[str, str]]:
        """Generate learning resource links"""
        links = []
        for rec in recommendations:
            links.append({
                "skill": rec.skill,
                "title": f"Learn {rec.skill}",
                "url": rec.learning_link,
                "provider": "LinkedIn Learning" if "linkedin.com" in rec.learning_link else "Microsoft Learn"
            })
        return links
    
    def _generate_summary(self, analysis, learning_mode: LearningMode) -> str:
        """Generate newsletter summary"""
        score = analysis.career_readiness.overall_score
        missing_count = len(analysis.career_readiness.missing_skills)
        
        mode_text = {
            LearningMode.CAREER_ADVANCEMENT: "career advancement",
            LearningMode.INTERNSHIP_PATH: "your internship path",
            LearningMode.TECH_REFRESH: "staying current with technology"
        }.get(learning_mode, "career growth")
        
        return f"Your career readiness score is {score:.1f}%. Focus on {missing_count} key skills to accelerate {mode_text}. This week's newsletter includes personalized code insights and actionable learning recommendations."
    
    def _render_newsletter(
        self,
        user_name: str,
        analysis,
        learning_links: list,
        learning_mode: LearningMode
    ) -> str:
        """Render newsletter HTML"""
        return self.newsletter_template.render(
            user_name=user_name,
            date=datetime.utcnow().strftime("%B %d, %Y"),
            career_readiness=analysis.career_readiness,
            code_insights=analysis.code_insights,
            skill_recommendations=analysis.skill_recommendations,
            learning_links=learning_links,
            learning_mode=learning_mode.value
        )
    
    def _load_template(self) -> Template:
        """Load newsletter HTML template"""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            line-height: 1.6; 
            color: #e5e7eb; 
            background-color: #030712;
            margin: 0;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background-color: #111827;
            border-radius: 8px;
            padding: 30px;
        }
        .header { 
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 8px; 
            margin-bottom: 30px;
            border: 1px solid #374151;
        }
        .header h1 {
            font-size: 2rem;
            margin: 0 0 10px 0;
            font-weight: bold;
        }
        .section { 
            margin: 30px 0; 
            padding: 20px; 
            background: #1f2937; 
            border: 1px solid #374151;
            border-radius: 8px; 
        }
        .section h2 {
            color: #9ca3af;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 20px;
        }
        .section h3 {
            color: #d1d5db;
            font-size: 1rem;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .score { 
            font-size: 48px; 
            font-weight: bold; 
            margin: 10px 0;
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .insight { 
            background: #111827; 
            padding: 15px; 
            margin: 15px 0; 
            border-left: 4px solid #8b5cf6; 
            border-radius: 4px;
            border: 1px solid #374151;
        }
        .insight h4 {
            color: #8b5cf6;
            font-size: 0.875rem;
            margin-bottom: 10px;
        }
        .insight pre {
            background: #030712;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            color: #d1d5db;
            border: 1px solid #374151;
            font-size: 0.75rem;
        }
        .skill-card { 
            background: #111827; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px;
            border: 1px solid #374151;
        }
        .skill-card h3 {
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        .link-button { 
            display: inline-block; 
            padding: 10px 20px; 
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            margin-top: 10px;
            font-size: 0.875rem;
        }
        .link-button:hover {
            opacity: 0.9;
        }
        .footer { 
            text-align: center; 
            margin-top: 40px; 
            padding: 20px; 
            color: #6b7280;
            border-top: 1px solid #374151;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        ul li {
            padding: 5px 0;
            color: #d1d5db;
        }
        ul li:before {
            content: "→ ";
            color: #8b5cf6;
        }
        a {
            color: #8b5cf6;
            text-decoration: none;
        }
        a:hover {
            color: #ec4899;
        }
        p {
            color: #d1d5db;
        }
        strong {
            color: #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Devbrah Weekly Newsletter</h1>
            <p>Hello {{ user_name }}!</p>
            <p>Your personalized career growth insights for {{ date }}</p>
        </div>
        
        <div class="section">
            <h2>📊 Career Readiness Meter</h2>
            <div class="score">{{ "%.1f"|format(career_readiness.overall_score) }}%</div>
            <p><strong>Skill Alignment:</strong> {{ "%.1f"|format(career_readiness.skill_alignment) }}%</p>
            <p><strong>Code Quality Score:</strong> {{ "%.1f"|format(career_readiness.code_quality_score) }}%</p>
            
            <h3>Your Strong Skills:</h3>
            <ul>
                {% for skill in career_readiness.strong_skills %}
                <li>{{ skill }}</li>
                {% endfor %}
            </ul>
            
            <h3>Skills to Develop:</h3>
            <ul>
                {% for skill in career_readiness.missing_skills %}
                <li>{{ skill }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="section">
            <h2>🧩 Personal Code Insights</h2>
            {% for insight in code_insights %}
            <div class="insight">
                <h4>{{ insight.file_path }}</h4>
                <pre>{{ insight.code_snippet }}</pre>
                <p><strong>Feedback:</strong> {{ insight.feedback }}</p>
                <p><strong>Suggestion:</strong> {{ insight.suggestion }}</p>
                {% if insight.complexity %}
                <p><em>Complexity: {{ insight.complexity }}</em></p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>📈 Skill Recommendations</h2>
            {% for rec in skill_recommendations %}
            <div class="skill-card">
                <h3>{{ rec.skill }}</h3>
                <p><strong>Current Level:</strong> {{ rec.current_level }} → <strong>Target:</strong> {{ rec.target_level }}</p>
                {% if rec.demand_percentage %}
                <p><strong>Market Demand:</strong> {{ "%.0f"|format(rec.demand_percentage) }}% of target roles require this</p>
                {% endif %}
                <a href="{{ rec.learning_link }}" class="link-button">Start Learning →</a>
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>🔗 Quick Learning Links</h2>
            {% for link in learning_links %}
            <p><a href="{{ link.url }}">{{ link.title }}</a> - {{ link.provider }}</p>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Generated by Devbrah | Microsoft for Startups Track</p>
            <p>Keep coding, keep growing! 🚀</p>
        </div>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    async def get_preview(self, newsletter_id: str) -> Dict[str, Any]:
        """Get newsletter preview (mock for hackathon)"""
        # In production, this would fetch from database
        return {
            "newsletter_id": newsletter_id,
            "preview": "Newsletter preview available"
        }



