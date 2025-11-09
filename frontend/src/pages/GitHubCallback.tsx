import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiService } from '../services/api'

export default function GitHubCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const code = searchParams.get('code')
  const email = localStorage.getItem('pending_github_email')

  useEffect(() => {
    const handleCallback = async () => {
      if (!code) {
        navigate('/dashboard')
        return
      }

      try {
        const response = await apiService.handleGitHubCallback(code, email || '')
        localStorage.removeItem('pending_github_email')
        
        if (response && response.connected) {
          // Connection is stored in database, no need for localStorage
          // The Dashboard will fetch it from the API
          console.log('GitHub connected successfully:', response.username)
          // Add a flag to trigger refresh on dashboard
          sessionStorage.setItem('github_just_connected', 'true')
        }
        navigate('/dashboard', { replace: true })
      } catch (error: any) {
        console.error('GitHub callback error:', error)
        navigate('/dashboard', { replace: true })
      }
    }

    handleCallback()
  }, [code, email, navigate])

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <div className="text-center text-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Connecting GitHub...</p>
      </div>
    </div>
  )
}

