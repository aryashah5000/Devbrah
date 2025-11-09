import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status || 'Network Error'} ${error.config?.url}`)
    console.error('Error details:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface CareerGoal {
  target_role: string
  target_company?: string
  description?: string
}

export interface NewsletterRequest {
  user_email: string
  user_name: string
  github_username?: string
  linkedin_url?: string
  career_goal?: CareerGoal
  learning_mode?: 'career_advancement' | 'internship_path' | 'tech_refresh'
  send_email?: boolean
}

export interface NewsletterResponse {
  newsletter_id: string
  user_name: string
  generated_at: string
  career_readiness: {
    overall_score: number
    skill_alignment: number
    code_quality_score: number
    missing_skills: string[]
    strong_skills: string[]
  }
  code_insights: Array<{
    file_path: string
    code_snippet: string
    feedback: string
    suggestion: string
    complexity?: string
  }>
  skill_recommendations: Array<{
    skill: string
    current_level: string
    target_level: string
    demand_percentage?: number
    learning_link: string
    priority: number
  }>
  learning_links: Array<{
    skill: string
    title: string
    url: string
    provider: string
  }>
  html_content: string
  summary: string
}

export const apiService = {
  register: async (email: string, name: string, password: string) => {
    const response = await api.post('/api/users/register', { email, name, password })
    return response.data
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/users/login', { email, password })
    return response.data
  },

  getGitHubAuthUrl: async () => {
    const response = await api.get('/api/auth/github/authorize')
    return response.data
  },

  handleGitHubCallback: async (code: string, email: string) => {
    const response = await api.get(`/api/auth/github/callback?code=${code}&email=${encodeURIComponent(email)}`)
    return response.data
  },

  getLinkedInAuthUrl: async () => {
    const response = await api.get('/api/auth/linkedin/authorize')
    return response.data
  },

  handleLinkedInCallback: async (code: string, email: string) => {
    const response = await api.get(`/api/auth/linkedin/callback?code=${code}&email=${encodeURIComponent(email)}`)
    return response.data
  },

  connectGitHub: async (username: string) => {
    const response = await api.post('/api/integrations/github', { username })
    return response.data
  },

  connectLinkedIn: async (profile_url: string) => {
    const response = await api.post('/api/integrations/linkedin', { profile_url })
    return response.data
  },

  generateNewsletter: async (request: NewsletterRequest) => {
    const response = await api.post('/api/newsletter/generate', {
      user_email: request.user_email,
      user_name: request.user_name,
      github_username: request.github_username,
      linkedin_url: request.linkedin_url,
      career_goal: request.career_goal,
      learning_mode: request.learning_mode,
      send_email: request.send_email !== false, // Default to true
    })
    return response.data
  },

  getNewsletterPreview: async (newsletterId: string) => {
    const response = await api.get(`/api/newsletter/preview/${newsletterId}`)
    return response.data
  },

  getGoogleAuthUrl: async () => {
    const response = await api.get('/api/auth/google/authorize')
    return response.data
  },

  handleGoogleCallback: async (code: string) => {
    const response = await api.get(`/api/auth/google/callback?code=${code}`)
    return response.data
  },

  subscribe: async (email: string) => {
    const response = await api.post(`/api/subscription/subscribe?email=${encodeURIComponent(email)}`)
    return response.data
  },

  unsubscribe: async (email: string) => {
    const response = await api.post(`/api/subscription/unsubscribe?email=${encodeURIComponent(email)}`)
    return response.data
  },

  getSubscriptionStatus: async (email: string) => {
    const response = await api.get(`/api/subscription/status?email=${encodeURIComponent(email)}`)
    return response.data
  },

  sendWeeklyNewsletter: async (email: string) => {
    const response = await api.post(`/api/newsletter/send-weekly?email=${encodeURIComponent(email)}`)
    return response.data
  },

  getIntegrationsStatus: async (email: string) => {
    const response = await api.get(`/api/integrations/status?email=${encodeURIComponent(email)}`)
    return response.data
  },
}

export default api



