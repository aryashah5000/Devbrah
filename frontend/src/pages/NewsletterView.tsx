import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiService, NewsletterResponse } from '../services/api'

export default function NewsletterView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [newsletter, setNewsletter] = useState<NewsletterResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // For hackathon, we'll use the newsletter from localStorage or generate a demo
    const storedNewsletter = localStorage.getItem('currentNewsletter')
    if (storedNewsletter) {
      setNewsletter(JSON.parse(storedNewsletter))
      setLoading(false)
    } else {
      // Generate a demo newsletter
      generateDemoNewsletter()
    }
  }, [id])

  const generateDemoNewsletter = async () => {
    try {
      const response = await apiService.generateNewsletter({
        github_username: 'demo-dev',
        linkedin_url: 'linkedin.com/in/demo',
        career_goal: {
          target_role: 'Software Engineer',
          target_company: 'Meta',
        },
        learning_mode: 'career_advancement',
      })
      setNewsletter(response)
      localStorage.setItem('currentNewsletter', JSON.stringify(response))
    } catch (error) {
      console.error('Failed to load newsletter:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading newsletter...</p>
        </div>
      </div>
    )
  }

  if (!newsletter) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Newsletter not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-primary-500 hover:text-primary-600"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">📧 Newsletter</h1>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-primary-500 hover:text-primary-600"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div
          className="bg-white rounded-xl shadow-lg p-8"
          dangerouslySetInnerHTML={{ __html: newsletter.html_content }}
        />
      </div>
    </div>
  )
}



