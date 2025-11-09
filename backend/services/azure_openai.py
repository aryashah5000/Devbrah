"""
Azure OpenAI Service for devbrah
"""

import os
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

from models.schemas import SkillAnalysis, CareerReadiness, CodeInsight, SkillRecommendation

load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        # Default to mock mode if no credentials provided (perfect for hackathon)
        self.use_mock = os.getenv("USE_MOCK_AI", "true").lower() == "true" or not (self.endpoint and self.api_key)
        
        if not self.use_mock and self.endpoint and self.api_key:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        else:
            self.client = None
            self.use_mock = True  # Force mock mode if no client
    
    def is_configured(self) -> bool:
        return not self.use_mock and self.client is not None
    
    async def analyze_skills(
        self,
        github_data: Optional[Dict[str, Any]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None,
        career_goal: Optional[Any] = None
    ) -> SkillAnalysis:
        """Analyze user skills using Azure OpenAI"""
        
        if self.use_mock or not self.client:
            return self._generate_mock_analysis(career_goal)
        
        # Prepare prompt
        prompt = self._build_analysis_prompt(github_data, linkedin_data, career_goal)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert career coach and code reviewer. Analyze developer skills and provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._parse_analysis_response(result)
        
        except Exception as e:
            print(f"Azure OpenAI error: {e}")
            return self._generate_mock_analysis(career_goal)
    
    def _build_analysis_prompt(
        self,
        github_data: Optional[Dict],
        linkedin_data: Optional[Dict],
        career_goal: Optional[Any]
    ) -> str:
        """Build comprehensive prompt for skill analysis with real code and data"""
        prompt_parts = [
            "You are an expert career coach and code reviewer. Analyze this developer's skills comprehensively:"
        ]
        
        if career_goal:
            prompt_parts.append(f"\n🎯 Career Goal: {career_goal.target_role} at {career_goal.target_company or 'target company'}")
            if career_goal.description:
                prompt_parts.append(f"   Description: {career_goal.description}")
        
        if github_data:
            prompt_parts.append("\n📂 GitHub Analysis:")
            prompt_parts.append(f"- Username: {github_data.get('username', 'N/A')}")
            prompt_parts.append(f"- Repositories: {len(github_data.get('repositories', []))}")
            prompt_parts.append(f"- Languages used: {', '.join(list(github_data.get('languages', {}).keys())[:10])}")
            
            # Add code samples for analysis
            code_samples = github_data.get("code_samples", [])
            if code_samples:
                prompt_parts.append(f"\n📝 Code Samples to Analyze ({len(code_samples)} files):")
                for i, sample in enumerate(code_samples[:5], 1):  # Analyze top 5
                    prompt_parts.append(f"\n--- Code Sample {i} ---")
                    prompt_parts.append(f"Repository: {sample.get('repo', 'N/A')}")
                    prompt_parts.append(f"File: {sample.get('file_path', 'N/A')}")
                    prompt_parts.append(f"Language: {sample.get('language', 'N/A')}")
                    prompt_parts.append(f"Code:\n{sample.get('code_snippet', '')[:400]}")
            
            # Add recent commits
            commits = github_data.get("recent_commits", [])
            if commits:
                prompt_parts.append(f"\n📊 Recent Commits ({len(commits)}):")
                for commit in commits[:10]:
                    prompt_parts.append(f"- [{commit.get('repo', 'N/A')}] {commit.get('message', '')[:60]}")
        
        if linkedin_data:
            prompt_parts.append("\n💼 LinkedIn Profile:")
            prompt_parts.append(f"- Name: {linkedin_data.get('name', 'N/A')}")
            prompt_parts.append(f"- Headline: {linkedin_data.get('headline', 'N/A')}")
            
            skills = linkedin_data.get("skills", [])
            if skills:
                prompt_parts.append(f"- Skills: {', '.join(skills[:15])}")
            
            experiences = linkedin_data.get("experiences", [])
            if experiences:
                prompt_parts.append(f"\n💼 Work Experience ({len(experiences)} positions):")
                for exp in experiences[:5]:
                    prompt_parts.append(f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})")
                    if exp.get('description'):
                        prompt_parts.append(f"  {exp.get('description', '')[:100]}")
        
        prompt_parts.append("\n\n📋 Provide a detailed JSON analysis with:")
        prompt_parts.append("1. career_readiness: {overall_score (0-100), skill_alignment (0-100), code_quality_score (0-100), missing_skills: [], strong_skills: []}")
        prompt_parts.append("2. code_insights: Array of {file_path, code_snippet (first 200 chars), feedback (specific issue found), suggestion (how to fix), complexity (if applicable)}")
        prompt_parts.append("   - Analyze the actual code samples provided for inefficiencies, outdated patterns, security issues, or improvements")
        prompt_parts.append("   - Be specific: mention exact functions, patterns, or practices that need improvement")
        prompt_parts.append("3. skill_recommendations: Array of {skill, current_level, target_level, demand_percentage (0-100), learning_link (actual Microsoft Learn or LinkedIn Learning course URL), priority (1-5)}")
        prompt_parts.append("   - Compare current skills with career goal requirements")
        prompt_parts.append("   - Identify outdated technologies that should be replaced")
        prompt_parts.append("   - Recommend new skills trending in the industry")
        prompt_parts.append("   - Prioritize based on career goal alignment")
        prompt_parts.append("   - IMPORTANT: Provide REAL course URLs from:")
        prompt_parts.append("     * LinkedIn Learning: https://www.linkedin.com/learning/ (e.g., https://www.linkedin.com/learning/react-js-essential-training)")
        prompt_parts.append("     * Microsoft Learn: https://learn.microsoft.com/en-us/training/ (e.g., https://learn.microsoft.com/en-us/training/paths/build-javascript-applications-typescript/)")
        prompt_parts.append("     * Do NOT use placeholder URLs - use actual course pages")
        
        prompt_parts.append("\nBe specific, actionable, and reference the actual code and experience data provided.")
        
        return "\n".join(prompt_parts)
    
    def _parse_analysis_response(self, result: Dict) -> SkillAnalysis:
        """Parse Azure OpenAI response into SkillAnalysis model"""
        career_readiness_data = result.get("career_readiness", {})
        career_readiness = CareerReadiness(**career_readiness_data)
        
        code_insights = [CodeInsight(**insight) for insight in result.get("code_insights", [])]
        
        # Parse skill recommendations and ensure real learning links
        skill_recommendations = []
        for rec in result.get("skill_recommendations", []):
            skill = rec.get("skill", "")
            # If learning_link is missing or looks like a placeholder, get a real one
            learning_link = rec.get("learning_link", "")
            if not learning_link or "placeholder" in learning_link.lower() or not ("linkedin.com/learning" in learning_link or "learn.microsoft.com" in learning_link):
                learning_link = self._get_learning_link(skill)
            
            skill_recommendations.append(SkillRecommendation(
                skill=skill,
                current_level=rec.get("current_level", "Beginner"),
                target_level=rec.get("target_level", "Intermediate"),
                demand_percentage=rec.get("demand_percentage", 50.0),
                learning_link=learning_link,
                priority=rec.get("priority", 3)
            ))
        
        return SkillAnalysis(
            career_readiness=career_readiness,
            code_insights=code_insights,
            skill_recommendations=skill_recommendations,
            analysis_date=datetime.utcnow()
        )
    
    def _get_learning_link(self, skill: str) -> str:
        """Get actual learning course URL for a skill"""
        skill_lower = skill.lower()
        
        # LinkedIn Learning courses
        linkedin_courses = {
            "react": "https://www.linkedin.com/learning/react-js-essential-training",
            "react hooks": "https://www.linkedin.com/learning/react-hooks",
            "typescript": "https://www.linkedin.com/learning/typescript-essential-training",
            "graphql": "https://www.linkedin.com/learning/graphql-essential-training",
            "python": "https://www.linkedin.com/learning/python-essential-training-1",
            "javascript": "https://www.linkedin.com/learning/javascript-essential-training",
            "node.js": "https://www.linkedin.com/learning/node-js-essential-training",
            "nodejs": "https://www.linkedin.com/learning/node-js-essential-training",
            "aws": "https://www.linkedin.com/learning/aws-essential-training-for-developers",
            "docker": "https://www.linkedin.com/learning/docker-essential-training-2",
            "kubernetes": "https://www.linkedin.com/learning/kubernetes-essential-training-application-development",
            "git": "https://www.linkedin.com/learning/git-essential-training",
            "sql": "https://www.linkedin.com/learning/sql-essential-training",
            "mongodb": "https://www.linkedin.com/learning/mongodb-essential-training",
            "postgresql": "https://www.linkedin.com/learning/postgresql-essential-training",
            "redis": "https://www.linkedin.com/learning/redis-essential-training",
            "fastapi": "https://www.linkedin.com/learning/building-restful-apis-with-fastapi",
            "django": "https://www.linkedin.com/learning/django-essential-training",
            "flask": "https://www.linkedin.com/learning/flask-essential-training",
            "vue.js": "https://www.linkedin.com/learning/vue-js-essential-training",
            "angular": "https://www.linkedin.com/learning/angular-essential-training",
            "next.js": "https://www.linkedin.com/learning/next-js-essential-training",
            "tailwind css": "https://www.linkedin.com/learning/tailwind-css-essential-training",
            "css": "https://www.linkedin.com/learning/css-essential-training",
            "html": "https://www.linkedin.com/learning/html-essential-training",
            "java": "https://www.linkedin.com/learning/java-essential-training",
            "c++": "https://www.linkedin.com/learning/c-plus-plus-essential-training",
            "c#": "https://www.linkedin.com/learning/c-sharp-essential-training",
            "go": "https://www.linkedin.com/learning/learning-go",
            "rust": "https://www.linkedin.com/learning/rust-essential-training",
            "machine learning": "https://www.linkedin.com/learning/machine-learning-essential-training",
            "ai": "https://www.linkedin.com/learning/artificial-intelligence-foundations-machine-learning",
            "tensorflow": "https://www.linkedin.com/learning/tensorflow-essential-training",
            "pytorch": "https://www.linkedin.com/learning/pytorch-essential-training",
            "data structures": "https://www.linkedin.com/learning/programming-foundations-data-structures",
            "algorithms": "https://www.linkedin.com/learning/introduction-to-algorithms",
            "system design": "https://www.linkedin.com/learning/system-design-for-developers",
            "microservices": "https://www.linkedin.com/learning/microservices-foundations",
            "rest api": "https://www.linkedin.com/learning/rest-api-design",
            "api": "https://www.linkedin.com/learning/rest-api-design",
        }
        
        # Microsoft Learn courses
        microsoft_courses = {
            "azure": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/",
            "azure functions": "https://learn.microsoft.com/en-us/training/paths/create-serverless-applications/",
            ".net": "https://learn.microsoft.com/en-us/training/paths/dotnet/",
            "c#": "https://learn.microsoft.com/en-us/training/paths/csharp-first-steps/",
            "asp.net": "https://learn.microsoft.com/en-us/training/paths/build-web-apps-aspnet-core/",
            "powershell": "https://learn.microsoft.com/en-us/training/paths/powershell/",
            "typescript": "https://learn.microsoft.com/en-us/training/paths/build-javascript-applications-typescript/",
            "javascript": "https://learn.microsoft.com/en-us/training/paths/web-development-101/",
            "python": "https://learn.microsoft.com/en-us/training/paths/beginner-python/",
            "git": "https://learn.microsoft.com/en-us/training/paths/intro-to-vc-git/",
            "docker": "https://learn.microsoft.com/en-us/training/paths/docker-containers/",
            "kubernetes": "https://learn.microsoft.com/en-us/training/paths/aks-fundamentals/",
            "sql": "https://learn.microsoft.com/en-us/training/paths/get-started-querying-with-transact-sql/",
            "sql server": "https://learn.microsoft.com/en-us/training/paths/sql-fundamentals/",
            "machine learning": "https://learn.microsoft.com/en-us/training/paths/build-ai-solutions-with-azure-ml/",
            "ai": "https://learn.microsoft.com/en-us/training/paths/get-started-with-artificial-intelligence-on-azure/",
            "data science": "https://learn.microsoft.com/en-us/training/paths/data-science/",
            "devops": "https://learn.microsoft.com/en-us/training/paths/az-400-describe-design-implement-devops-processes/",
            "security": "https://learn.microsoft.com/en-us/training/paths/describe-security-concepts-methodologies/",
        }
        
        # Check LinkedIn Learning first (more comprehensive)
        for key, url in linkedin_courses.items():
            if key in skill_lower:
                return url
        
        # Check Microsoft Learn
        for key, url in microsoft_courses.items():
            if key in skill_lower:
                return url
        
        # Default fallback - search LinkedIn Learning
        return f"https://www.linkedin.com/learning/search?keywords={skill.replace(' ', '%20')}"
    
    def _generate_mock_analysis(self, career_goal: Optional[Any]) -> SkillAnalysis:
        """Generate mock analysis for demo purposes"""
        target_role = career_goal.target_role if career_goal else "Software Engineer"
        
        return SkillAnalysis(
            career_readiness=CareerReadiness(
                overall_score=72.5,
                skill_alignment=68.0,
                code_quality_score=75.0,
                missing_skills=["React Hooks", "TypeScript", "GraphQL"],
                strong_skills=["Python", "JavaScript", "Git", "REST APIs"]
            ),
            code_insights=[
                CodeInsight(
                    file_path="src/utils/sorter.py",
                    code_snippet="def sort_data(data):\n    for i in range(len(data)):\n        for j in range(i+1, len(data)):\n            if data[i] > data[j]:\n                data[i], data[j] = data[j], data[i]",
                    feedback="This sorting function has O(n²) complexity",
                    suggestion="Use Python's built-in sorted() with a key function to simplify and improve performance",
                    complexity="O(n²)"
                ),
                CodeInsight(
                    file_path="api/routes.py",
                    code_snippet="from flask import Flask\napp = Flask(__name__)",
                    feedback="Using Flask for async operations",
                    suggestion="Consider switching to FastAPI — many modern roles favor async backends with better performance",
                    complexity=None
                )
            ],
            skill_recommendations=[
                SkillRecommendation(
                    skill="React Hooks",
                    current_level="Beginner",
                    target_level="Advanced",
                    demand_percentage=68.0,
                    learning_link=self._get_learning_link("React Hooks"),
                    priority=1
                ),
                SkillRecommendation(
                    skill="TypeScript",
                    current_level="None",
                    target_level="Intermediate",
                    demand_percentage=75.0,
                    learning_link=self._get_learning_link("TypeScript"),
                    priority=2
                ),
                SkillRecommendation(
                    skill="GraphQL",
                    current_level="None",
                    target_level="Intermediate",
                    demand_percentage=45.0,
                    learning_link=self._get_learning_link("GraphQL"),
                    priority=3
                )
            ],
            analysis_date=datetime.utcnow()
        )

