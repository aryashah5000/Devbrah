import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService, NewsletterResponse } from '../services/api'

export default function Subscription() {
  const [subscribed, setSubscribed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [targetRole, setTargetRole] = useState('Software Engineer')
  const [targetCompany, setTargetCompany] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [learningMode, setLearningMode] = useState<'career_advancement' | 'internship_path' | 'tech_refresh'>('career_advancement')
  const [newsletter, setNewsletter] = useState<NewsletterResponse | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.email) {
      navigate('/')
      return
    }

    // Check subscription status
    const checkStatus = async () => {
      try {
        const response = await apiService.getSubscriptionStatus(user.email)
        setSubscribed(response.subscribed)
      } catch (error) {
        console.error('Failed to check subscription status:', error)
      }
    }
    checkStatus()
  }, [navigate])

  const handleSubscribe = async () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.email) {
      navigate('/')
      return
    }

    setLoading(true)
    try {
      if (subscribed) {
        await apiService.unsubscribe(user.email)
        setSubscribed(false)
      } else {
        await apiService.subscribe(user.email)
        setSubscribed(true)
      }
    } catch (error: any) {
      console.error('Failed to update subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAndSendNewsletter = async () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.email) {
      navigate('/')
      return
    }

    if (!subscribed) {
      return
    }

    if (!targetRole.trim()) {
      return
    }

    setSending(true)
    try {
      const response = await apiService.generateNewsletter({
        user_email: user.email,
        user_name: user.name || user.email.split('@')[0],
        github_username: undefined,
        linkedin_url: undefined,
        career_goal: {
          target_role: targetRole,
          target_company: targetCompany || undefined,
          description: jobDescription || undefined,
        },
        learning_mode: learningMode,
        send_email: true,
      })
      setNewsletter(response)
      localStorage.setItem('currentNewsletter', JSON.stringify(response))
      alert('✅ Newsletter generated and sent to your email! Check your inbox.')
    } catch (error: any) {
      console.error('Failed to generate newsletter:', error)
    } finally {
      setSending(false)
    }
  }

  const user = JSON.parse(localStorage.getItem('user') || '{}')

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-mono font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Devbrah
            </h1>
            <div className="h-6 w-px bg-gray-700"></div>
            <span className="text-sm text-gray-400 font-mono">Newsletter Subscription</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-3 py-1.5 text-xs font-mono bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded transition"
            >
              Dashboard
            </button>
            <button
              onClick={() => {
                localStorage.clear()
                navigate('/')
              }}
              className="px-3 py-1.5 text-xs font-mono bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Subscription Status */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">SUBSCRIPTION STATUS</h3>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-mono font-semibold mb-2 text-gray-100">
                  {subscribed ? '✅ Subscribed' : '❌ Not Subscribed'}
                </h3>
                <p className="text-sm text-gray-400 font-mono">
                  {subscribed
                    ? `You will receive weekly newsletters at ${user.email}`
                    : 'Subscribe to start receiving personalized career insights'}
                </p>
              </div>
            </div>
          </div>

          {/* Subscribe/Unsubscribe Button */}
          <button
            onClick={handleSubscribe}
            disabled={loading}
            className={`w-full py-3 rounded-lg font-mono text-sm font-semibold transition disabled:opacity-50 ${
              subscribed
                ? 'bg-red-600/20 border border-red-500/30 text-red-300 hover:bg-red-600/30'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg'
            }`}
          >
            {loading
              ? 'Processing...'
              : subscribed
              ? '🔔 Unsubscribe'
              : '📧 Subscribe to Newsletter'}
          </button>

          {/* Career Goals & Newsletter Generation */}
          {subscribed && (
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
                <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">CAREER GOALS</h3>
                <p className="text-sm text-gray-400 mb-4 font-mono">
                  Tell us about your career goals so we can personalize your newsletter
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                      TARGET ROLE *
                    </label>
                    <input
                      type="text"
                      value={targetRole}
                      onChange={(e) => setTargetRole(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                      placeholder="Software Engineer, Data Scientist, etc."
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                      TARGET COMPANY (OPTIONAL)
                    </label>
                    <input
                      type="text"
                      value={targetCompany}
                      onChange={(e) => setTargetCompany(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                      placeholder="Meta, Microsoft, Google, etc."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                      JOB DESCRIPTION / CAREER GOAL (OPTIONAL)
                    </label>
                    <textarea
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                      placeholder="Describe what you're aiming for, e.g., 'I want to become a senior full-stack developer at a tech startup'"
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                      LEARNING MODE
                    </label>
                    <select
                      value={learningMode}
                      onChange={(e) => setLearningMode(e.target.value as any)}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                    >
                      <option value="career_advancement">Career Advancement</option>
                      <option value="internship_path">Internship Path</option>
                      <option value="tech_refresh">Tech Refresh</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
                <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">GENERATE & SEND NEWSLETTER</h3>
                <p className="text-sm text-gray-400 mb-4 font-mono">
                  Generate a personalized newsletter based on your GitHub/LinkedIn activity and career goals, then send it to your email
                </p>
                <button
                  onClick={handleGenerateAndSendNewsletter}
                  disabled={sending || !targetRole.trim()}
                  className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white py-3 rounded-lg font-mono text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {sending ? '🔄 Generating & Sending...' : '🚀 Generate & Send Newsletter'}
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center font-mono">
                  Make sure you've connected at least one account (GitHub or LinkedIn) on the Dashboard
                </p>
                
                {newsletter && (
                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <div className="bg-green-600/20 border border-green-500/30 rounded-lg p-4 mb-4">
                      <p className="text-sm text-green-300 mb-2 font-mono">
                        ✅ Newsletter generated successfully!
                      </p>
                      <p className="text-xs text-green-400 font-mono">
                        Career Readiness Score: <strong>{newsletter.career_readiness.overall_score.toFixed(1)}%</strong>
                      </p>
                    </div>
                    <button
                      onClick={() => navigate(`/full-report?mode=${learningMode}`)}
                      className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-2 rounded-lg font-mono text-sm font-semibold transition-colors"
                    >
                      📊 View Full Report
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Benefits */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">WHAT YOU'LL GET:</h3>
            <ul className="space-y-2 text-sm text-gray-300 font-mono">
              <li className="flex items-start gap-2">
                <span className="text-green-400">→</span>
                <span>Personalized code insights and feedback</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400">→</span>
                <span>Skill recommendations based on your career goals</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400">→</span>
                <span>Career readiness score and progress tracking</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400">→</span>
                <span>Direct links to learning resources</span>
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}
