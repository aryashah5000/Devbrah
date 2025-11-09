# 🚀 Quick Hackathon Setup Guide

## ⚡ Fast Setup (5 minutes)

### 1. Backend Setup

```bash
cd backend

# Windows
start.bat

# Mac/Linux
chmod +x start.sh
./start.sh
```

**OR manually:**

```bash
cd backend
pip install -r requirements.txt

# Copy .env.example to .env (optional - works without Azure OpenAI in mock mode)
cp .env.example .env

# Start server
uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Windows
start.bat

# Mac/Linux
npm install
npm run dev
```

**OR manually:**

```bash
cd frontend
npm install
npm run dev
```

## 🎯 Demo Mode

The app works **out of the box** in mock mode without Azure OpenAI:

1. Backend runs with `USE_MOCK_AI=true` by default (if no Azure credentials)
2. All AI responses are realistic mock data
3. Perfect for hackathon demos!

## 🔑 Using Azure OpenAI (Optional)

If you have Azure OpenAI credentials:

1. Update `backend/.env`:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   USE_MOCK_AI=false
   ```

2. Restart the backend server

## 🎨 Demo Flow

1. **Login**: Use `demo@devbrah.ai` / `demo123`
2. **Connect Accounts**: 
   - GitHub: `demo-dev`
   - LinkedIn: `linkedin.com/in/demo`
3. **Set Career Goal**: 
   - Role: "Software Engineer"
   - Company: "Meta"
4. **Generate Newsletter**: Click "Generate Newsletter"
5. **View Results**: See personalized insights and recommendations

## 📊 What You'll See

- ✅ Career Readiness Score (0-100%)
- ✅ Code Insights with specific feedback
- ✅ Skill Recommendations with learning links
- ✅ Beautiful HTML newsletter
- ✅ Microsoft Learn / LinkedIn Learning integration

## 🏆 Hackathon Presentation Tips

1. **Show the Flow**: Login → Connect → Generate → View Newsletter
2. **Highlight Microsoft Integration**: Azure OpenAI, Microsoft Learn links
3. **Emphasize Personalization**: Real code analysis, skill gaps
4. **Business Model**: Subscription SaaS ($10/month)
5. **Scalability**: Ready for production with real OAuth

## 🐛 Troubleshooting

- **Backend won't start**: Make sure Python 3.10+ is installed
- **Frontend won't start**: Make sure Node.js 18+ is installed
- **CORS errors**: Check that backend is running on port 8000
- **No data**: Make sure you've connected at least one account (GitHub or LinkedIn)

## 📝 Notes

- All data is mocked for hackathon demo
- No real OAuth integration (would need production setup)
- Database uses SQLite (can scale to PostgreSQL)
- Newsletter is generated in real-time

Good luck with your hackathon! 🚀



