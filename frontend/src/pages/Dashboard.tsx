import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { apiService } from '../services/api'

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [githubConnected, setGithubConnected] = useState(false)
  const [linkedinConnected, setLinkedinConnected] = useState(false)
  const [githubUsername, setGithubUsername] = useState('')
  const [linkedinName, setLinkedinName] = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const fetchConnectionStatus = useCallback(async () => {
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      navigate('/')
      return
    }
    
    try {
      const user = JSON.parse(userStr)
      if (user.email) {
        const status = await apiService.getIntegrationsStatus(user.email)
        
        if (status.github?.connected) {
          setGithubConnected(true)
          setGithubUsername(status.github.username || '')
        } else {
          setGithubConnected(false)
          setGithubUsername('')
          // Clear localStorage for this user
          localStorage.removeItem('github_connected')
          localStorage.removeItem('github_username')
        }
        
        if (status.linkedin?.connected) {
          setLinkedinConnected(true)
          setLinkedinName(status.linkedin.name || '')
        } else {
          setLinkedinConnected(false)
          setLinkedinName('')
          // Clear localStorage for this user
          localStorage.removeItem('linkedin_connected')
          localStorage.removeItem('linkedin_name')
        }
      }
    } catch (error) {
      console.error('Failed to fetch connection status:', error)
      // On error, clear all connection status
      setGithubConnected(false)
      setLinkedinConnected(false)
      setGithubUsername('')
      setLinkedinName('')
    }
  }, [navigate])

  useEffect(() => {
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      navigate('/')
      return
    }
    
    // Fetch connection status on mount
    fetchConnectionStatus()
    
    // Also listen for focus events to refetch when returning from OAuth
    const handleFocus = () => {
      // Only refetch if we're on the dashboard
      if (location.pathname === '/dashboard') {
        fetchConnectionStatus()
      }
    }
    
    window.addEventListener('focus', handleFocus)
    
    return () => {
      window.removeEventListener('focus', handleFocus)
    }
  }, [navigate, fetchConnectionStatus, location.pathname])

  // Separate effect to handle OAuth callback returns
  useEffect(() => {
    // Check if we just returned from OAuth callback
    const githubJustConnected = sessionStorage.getItem('github_just_connected') === 'true'
    const linkedinJustConnected = sessionStorage.getItem('linkedin_just_connected') === 'true'
    
    if (githubJustConnected || linkedinJustConnected) {
      sessionStorage.removeItem('github_just_connected')
      sessionStorage.removeItem('linkedin_just_connected')
      // Small delay to ensure database is updated, then refetch
      setTimeout(() => {
        fetchConnectionStatus()
      }, 500)
    }
  }, [location.pathname, fetchConnectionStatus])

  const connectGitHub = async () => {
    setLoading(true)
    try {
      const response = await apiService.getGitHubAuthUrl()
      // Store user email for callback
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      localStorage.setItem('pending_github_email', user.email || '')
      // Redirect to GitHub OAuth
      window.location.href = response.authorization_url
    } catch (error: any) {
      console.error('Failed to initiate GitHub login:', error)
      setLoading(false)
    }
  }

  const connectLinkedIn = async () => {
    setLoading(true)
    try {
      const response = await apiService.getLinkedInAuthUrl()
      // Store user email for callback
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      localStorage.setItem('pending_linkedin_email', user.email || '')
      // Redirect to LinkedIn OAuth
      window.location.href = response.authorization_url
    } catch (error: any) {
      console.error('Failed to initiate LinkedIn login:', error)
      setLoading(false)
    }
  }


  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-mono font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Devbrah
            </h1>
            <div className="h-6 w-px bg-gray-700"></div>
            <span className="text-sm text-gray-400 font-mono">Dashboard</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/subscription')}
              className="px-3 py-1.5 text-xs font-mono bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded transition"
            >
              📧 Subscription
            </button>
            <button
              onClick={() => {
                // Clear all user data including connection status
                localStorage.removeItem('user')
                  localStorage.removeItem('token')
                  localStorage.removeItem('github_connected')
                  localStorage.removeItem('github_username')
                  localStorage.removeItem('linkedin_connected')
                  localStorage.removeItem('linkedin_name')
                  navigate('/')
                }}
                className="px-3 py-1.5 text-xs font-mono bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded transition"
              >
                Logout
              </button>
            </div>
          </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Configuration */}
          <div className="space-y-6">
            {/* GitHub Integration */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
              <h2 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">GITHUB INTEGRATION</h2>
              <div className="space-y-4">
                {githubConnected && githubUsername && (
                  <div className="bg-green-600/20 border border-green-500/30 rounded-lg p-3">
                    <p className="text-sm text-green-300 font-mono">
                      ✓ Connected as <strong>{githubUsername}</strong>
                    </p>
                  </div>
                )}
                <button
                  onClick={connectGitHub}
                  disabled={loading || githubConnected}
                  className={`w-full py-3 rounded-lg font-mono text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${
                    githubConnected
                      ? 'bg-green-600/20 border border-green-500/30 text-green-300 cursor-not-allowed'
                      : 'bg-gray-800 border border-gray-700 text-white hover:bg-gray-700'
                  } disabled:opacity-50`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  {githubConnected ? '✓ GitHub Connected' : 'Login with GitHub'}
                </button>
                <p className="text-xs text-gray-500 text-center font-mono">
                  Connect your GitHub to analyze your code and commits
                </p>
              </div>
            </div>

            {/* LinkedIn Integration */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
              <h2 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">LINKEDIN INTEGRATION</h2>
              <div className="space-y-4">
                {linkedinConnected && linkedinName && (
                  <div className="bg-green-600/20 border border-green-500/30 rounded-lg p-3">
                    <p className="text-sm text-green-300 font-mono">
                      ✓ Connected as <strong>{linkedinName}</strong>
                    </p>
                  </div>
                )}
                <button
                  onClick={connectLinkedIn}
                  disabled={loading || linkedinConnected}
                  className={`w-full py-3 rounded-lg font-mono text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${
                    linkedinConnected
                      ? 'bg-green-600/20 border border-green-500/30 text-green-300 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-500 border border-blue-500'
                  } disabled:opacity-50`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  {linkedinConnected ? '✓ LinkedIn Connected' : 'Login with LinkedIn'}
                </button>
                <p className="text-xs text-gray-500 text-center font-mono">
                  Connect your LinkedIn to analyze your skills and experience
                </p>
              </div>
            </div>

            {/* Info Card */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
              <h2 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">READY TO GET YOUR NEWSLETTER?</h2>
              <p className="text-sm text-gray-400 mb-4 font-mono">
                Connect your accounts above, then go to the Subscription page to set your career goals and generate your personalized newsletter!
              </p>
              <button
                onClick={() => navigate('/subscription')}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-2 rounded-lg font-mono text-sm font-semibold transition-colors"
              >
                Go to Subscription →
              </button>
            </div>
          </div>

          {/* Right Column - Connection Status */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl text-center">
              <div className="text-4xl mb-4">🔗</div>
              <h3 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">
                CONNECTION STATUS
              </h3>
              <p className="text-sm text-gray-400 mb-6 font-mono">
                Link your GitHub and LinkedIn accounts to enable personalized newsletter generation
              </p>
              <div className="space-y-3">
                <div className={`p-4 rounded-lg border ${githubConnected ? 'bg-green-600/20 border-green-500/30' : 'bg-gray-800/50 border-gray-700'}`}>
                  <p className="font-mono font-semibold text-sm text-gray-100">
                    {githubConnected ? '✅ GitHub Connected' : '❌ GitHub Not Connected'}
                  </p>
                  {githubConnected && githubUsername && (
                    <p className="text-xs text-gray-400 mt-1 font-mono">as {githubUsername}</p>
                  )}
                </div>
                <div className={`p-4 rounded-lg border ${linkedinConnected ? 'bg-green-600/20 border-green-500/30' : 'bg-gray-800/50 border-gray-700'}`}>
                  <p className="font-mono font-semibold text-sm text-gray-100">
                    {linkedinConnected ? '✅ LinkedIn Connected' : '❌ LinkedIn Not Connected'}
                  </p>
                  {linkedinConnected && linkedinName && (
                    <p className="text-xs text-gray-400 mt-1 font-mono">as {linkedinName}</p>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-6 font-mono">
                After connecting accounts, go to the Subscription page to set your career goals and generate your newsletter!
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

