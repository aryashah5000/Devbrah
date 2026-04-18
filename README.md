# 🚀 Devbrah - Personalized AI Career Growth Newsletter

**Microsoft for Startups Track - Hackathon Project**

Devbrah is a personalized, subscription-based weekly newsletter powered by Azure OpenAI that helps developers and professionals continuously grow in their technical careers.

## 🎯 Hackathon Alignment

This project leverages **Microsoft for Startups** tools and services:
- **Azure OpenAI** - Core AI engine for code analysis and newsletter generation
- **GitHub Integration** - Analyzes real coding activity (using GitHub API)
- **LinkedIn Integration** - Professional profile analysis (OAuth ready)
- **Microsoft Learn Integration** - Learning resource recommendations
- **Viable Startup Business Model** - Subscription SaaS with clear monetization

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Azure OpenAI** - GPT-4 for intelligent analysis
- **SQLite** - Lightweight database (can scale to PostgreSQL)
- **Pydantic** - Data validation
- **Jinja2** - Newsletter template rendering

### Frontend
- **React** - Modern UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Beautiful, responsive design
- **Vite** - Fast build tool

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Azure OpenAI API key (or use mock mode for demo)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"

# Run the server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Mock Mode (No Azure OpenAI Required)

Set `USE_MOCK_AI=true` in backend `.env` to use mock AI responses for demo purposes. This is perfect for hackathon demos when you don't have Azure OpenAI credentials yet!

## 📁 Project Structure

```
devbrah/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   ├── azure_openai.py  # Azure OpenAI integration
│   │   ├── github_service.py # GitHub data fetching (mock)
│   │   ├── linkedin_service.py # LinkedIn data fetching (mock)
│   │   └── newsletter_service.py # Newsletter generation
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── templates/
│       └── newsletter.html  # Newsletter template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── services/        # API clients
└── README.md
```

## 🎨 Features

- ✅ **GitHub Code Analysis** - Analyzes commits, PRs, and repositories
- ✅ **LinkedIn Profile Analysis** - Skills and experience matching
- ✅ **AI-Powered Insights** - Personalized code feedback and recommendations
- ✅ **Career Readiness Meter** - Visual skill alignment tracking
- ✅ **Learning Resource Links** - Direct links to Microsoft Learn, LinkedIn Learning
- ✅ **Weekly Newsletter** - Automated personalized newsletters

## 💡 Demo Credentials

For hackathon demo, use:
- Email: `demo@devbrah.ai`
- Password: `demo123`

## 🏆 Hackathon Submission Highlights

1. **Microsoft Integration**: Deep Azure OpenAI integration for intelligent analysis
2. **Real-World Problem**: Addresses developer career growth pain point
3. **Viable Business Model**: Clear subscription + affiliate revenue model
4. **Scalable Architecture**: Ready for production deployment
5. **Beautiful UI**: Modern, responsive design

## 📝 License

MIT License - Hackathon Project

