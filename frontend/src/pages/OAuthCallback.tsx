import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiService } from '../services/api'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const code = searchParams.get('code')

  useEffect(() => {
    const handleCallback = async () => {
      if (!code) {
        navigate('/')
        return
      }

      try {
        const response = await apiService.handleGoogleCallback(code)
        if (response && response.user) {
          // Clear any previous user's connection status from localStorage
          localStorage.removeItem('github_connected')
          localStorage.removeItem('github_username')
          localStorage.removeItem('linkedin_connected')
          localStorage.removeItem('linkedin_name')
          
          localStorage.setItem('token', response.access_token || 'demo-token')
          localStorage.setItem('user', JSON.stringify(response.user))
          navigate('/dashboard')
        } else {
          navigate('/dashboard')
        }
      } catch (error: any) {
        console.error('OAuth callback error:', error)
        navigate('/dashboard')
      }
    }

    handleCallback()
  }, [code, navigate])

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <div className="text-center text-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Completing login...</p>
      </div>
    </div>
  )
}

