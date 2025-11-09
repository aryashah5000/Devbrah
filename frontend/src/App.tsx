import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import NewsletterView from './pages/NewsletterView'
import OAuthCallback from './pages/OAuthCallback'
import GitHubCallback from './pages/GitHubCallback'
import LinkedInCallback from './pages/LinkedInCallback'
import Subscription from './pages/Subscription'
import FullReport from './pages/FullReport'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/subscription" element={<Subscription />} />
        <Route path="/full-report" element={<FullReport />} />
        <Route path="/newsletter/:id" element={<NewsletterView />} />
        <Route path="/auth/callback" element={<OAuthCallback />} />
        <Route path="/auth/github/callback" element={<GitHubCallback />} />
        <Route path="/auth/linkedin/callback" element={<LinkedInCallback />} />
      </Routes>
    </Router>
  )
}

export default App



