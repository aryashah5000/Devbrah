import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService } from '../services/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [isRegistering, setIsRegistering] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (isRegistering && !name.trim()) {
      alert('Please enter your name')
      return
    }
    if (!email.trim()) {
      alert('Please enter your email')
      return
    }
    if (!password.trim()) {
      alert('Please enter your password')
      return
    }
    if (password.length < 6) {
      alert('Password must be at least 6 characters')
      return
    }
    
    setLoading(true)

    try {
      if (isRegistering) {
        const registerResponse = await apiService.register(email, name, password)
        console.log('Registration successful:', registerResponse)
        // After successful registration, automatically log in
      }
      const response = await apiService.login(email, password)
      console.log('Login successful:', response)
      
      if (response && response.user && response.access_token) {
        // Clear any previous user's connection status from localStorage
        localStorage.removeItem('github_connected')
        localStorage.removeItem('github_username')
        localStorage.removeItem('linkedin_connected')
        localStorage.removeItem('linkedin_name')
        
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        navigate('/dashboard')
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (error: any) {
      console.error(isRegistering ? 'Registration error:' : 'Login error:', error)
      console.error('Error response:', error.response)
      
      let errorMessage = 'An error occurred'
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      } else if (error.response?.statusText) {
        errorMessage = `${error.response.status}: ${error.response.statusText}`
      }
      
      if (errorMessage && errorMessage !== 'An error occurred') {
        alert(errorMessage)
      } else {
        alert(isRegistering ? 'Registration failed. Please try again.' : 'Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setLoading(true)
    try {
      const response = await apiService.getGoogleAuthUrl()
      // Redirect to Google OAuth
      window.location.href = response.authorization_url
    } catch (error: any) {
      console.error('Failed to initiate Google login:', error)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-5xl font-mono font-bold tracking-tight bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Devbrah
          </h1>
          <p className="text-sm text-gray-400">Personalized Career Growth Newsletter</p>
          <p className="text-xs text-gray-500 pt-2">AI-powered skill analysis and career insights</p>
        </div>

        <div className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegistering && (
              <div>
                <label htmlFor="name" className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                  NAME *
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                  required
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                EMAIL *
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-mono text-gray-400 mb-2 tracking-wider">
                PASSWORD *
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-sm font-mono focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg font-mono text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? 'Loading...' : isRegistering ? 'Register' : 'Login'}
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-800"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-gray-950 text-gray-500 font-mono">OR CONTINUE WITH</span>
            </div>
          </div>

          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-gray-900 border border-gray-700 text-gray-300 py-3 rounded-lg font-mono text-sm font-semibold hover:bg-gray-800 hover:border-gray-600 transition disabled:opacity-50"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>
        </div>

        <div className="text-center">
          <button
            onClick={() => setIsRegistering(!isRegistering)}
            className="text-xs text-gray-400 hover:text-gray-300 font-mono transition"
          >
            {isRegistering
              ? 'Already have an account? Login'
              : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  )
}
