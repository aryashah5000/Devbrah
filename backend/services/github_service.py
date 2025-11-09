"""
GitHub Service - Real GitHub API integration
"""

from typing import Dict, Any, List, Optional
import httpx
import base64
from datetime import datetime

class GitHubService:
    """Service for fetching real GitHub data"""
    
    def __init__(self):
        self.api_base = "https://api.github.com"
    
    async def fetch_user_data(self, access_token: str) -> Dict[str, Any]:
        """Fetch GitHub user data using OAuth token"""
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_resp = await client.get(f"{self.api_base}/user", headers=headers)
            user_data = user_resp.json()
            
            # Get repositories
            repos_resp = await client.get(f"{self.api_base}/user/repos?sort=updated&per_page=10", headers=headers)
            repos_data = repos_resp.json()
            
            # Get recent commits
            commits = await self._get_recent_commits(client, headers, repos_data[:5])
            
            # Get code samples from repositories
            code_samples = await self._get_code_samples(client, headers, repos_data[:5])
            
            return {
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "profile_url": user_data.get("html_url"),
                "repositories": self._format_repositories(repos_data),
                "recent_commits": commits,
                "code_samples": code_samples,
                "languages": self._analyze_languages(repos_data),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "created_at": user_data.get("created_at")
            }
    
    async def _get_recent_commits(self, client: httpx.AsyncClient, headers: dict, repos: List[Dict]) -> List[Dict[str, Any]]:
        """Get recent commits from repositories"""
        commits = []
        for repo in repos[:5]:  # Top 5 repos
            try:
                repo_name = repo["full_name"]
                commits_resp = await client.get(
                    f"{self.api_base}/repos/{repo_name}/commits?per_page=5",
                    headers=headers
                )
                if commits_resp.status_code == 200:
                    repo_commits = commits_resp.json()
                    for commit in repo_commits:
                        commits.append({
                            "sha": commit.get("sha", "")[:7],
                            "message": commit.get("commit", {}).get("message", ""),
                            "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                            "repo": repo_name,
                            "url": commit.get("html_url", "")
                        })
            except Exception:
                continue
        
        return sorted(commits, key=lambda x: x.get("date", ""), reverse=True)[:20]
    
    async def _get_code_samples(self, client: httpx.AsyncClient, headers: dict, repos: List[Dict]) -> List[Dict[str, Any]]:
        """Get code samples from repositories for analysis"""
        code_samples = []
        for repo in repos[:5]:  # Top 5 repos
            try:
                repo_name = repo["full_name"]
                # Get repository contents (main files)
                contents_resp = await client.get(
                    f"{self.api_base}/repos/{repo_name}/contents",
                    headers=headers
                )
                if contents_resp.status_code == 200:
                    contents = contents_resp.json()
                    for item in contents[:10]:  # First 10 files
                        if item.get("type") == "file" and self._is_code_file(item.get("name", "")):
                            try:
                                file_resp = await client.get(item.get("url", ""), headers=headers)
                                if file_resp.status_code == 200:
                                    file_data = file_resp.json()
                                    content = base64.b64decode(file_data.get("content", "")).decode('utf-8', errors='ignore')
                                    # Get first 500 chars for analysis
                                    code_samples.append({
                                        "repo": repo_name,
                                        "file_path": item.get("path", ""),
                                        "language": item.get("name", "").split(".")[-1] if "." in item.get("name", "") else "unknown",
                                        "code_snippet": content[:500],
                                        "url": item.get("html_url", "")
                                    })
                            except Exception:
                                continue
            except Exception:
                continue
        
        return code_samples[:20]  # Limit to 20 samples
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file"""
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php', '.swift', '.kt']
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _format_repositories(self, repos_data: List[Dict]) -> List[Dict[str, Any]]:
        """Format repository data"""
        repos = []
        for repo in repos_data:
            repos.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url"),
                "updated_at": repo.get("updated_at"),
                "is_private": repo.get("private", False),
                "has_issues": repo.get("has_issues", False),
                "has_wiki": repo.get("has_wiki", False)
            })
        return repos
    
    def _analyze_languages(self, repos_data: List[Dict]) -> Dict[str, int]:
        """Analyze language usage from repositories"""
        languages = {}
        for repo in repos_data:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        return languages
