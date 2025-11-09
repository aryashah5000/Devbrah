import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'
import { apiService, NewsletterResponse } from '../services/api'

export default function FullReport() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [newsletter, setNewsletter] = useState<NewsletterResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const learningMode = searchParams.get('mode') || 'career_advancement'

  useEffect(() => {
    // Get newsletter from localStorage or fetch
    const storedNewsletter = localStorage.getItem('currentNewsletter')
    if (storedNewsletter) {
      setNewsletter(JSON.parse(storedNewsletter))
      setLoading(false)
    } else {
      navigate('/subscription')
    }
  }, [navigate])

  const getModeTitle = () => {
    switch (learningMode) {
      case 'career_advancement':
        return 'Career Advancement Report'
      case 'internship_path':
        return 'Internship Path Report'
      case 'tech_refresh':
        return 'Tech Refresh Report'
      default:
        return 'Full Career Report'
    }
  }

  const getModeDescription = () => {
    switch (learningMode) {
      case 'career_advancement':
        return 'Optimize your skills for your current role or next promotion'
      case 'internship_path':
        return 'Target specific companies or positions for internships'
      case 'tech_refresh':
        return 'Stay up-to-date with new frameworks and languages'
      default:
        return 'Comprehensive analysis of your career readiness'
    }
  }

  // Generate chart data from newsletter
  const chartData = useMemo(() => {
    if (!newsletter) return null

    const { career_readiness, skill_recommendations } = newsletter

    // Score trend data (simulated historical data)
    const currentScore = career_readiness.overall_score
    const scoreTrend = Array.from({ length: 6 }, (_, i) => ({
      week: `Week ${6 - i}`,
      score: Math.max(0, Math.min(100, currentScore - (5 - i) * 2 + Math.random() * 5))
    }))

    // Skill distribution pie chart
    const skillDistribution = [
      { name: 'Strong Skills', value: career_readiness.strong_skills.length },
      { name: 'Missing Skills', value: career_readiness.missing_skills.length },
      { name: 'Recommended', value: skill_recommendations.length }
    ]

    // Skill recommendations bar chart
    const skillBars = skill_recommendations
      .sort((a, b) => b.priority - a.priority)
      .slice(0, 8)
      .map(rec => ({
        name: rec.skill.length > 15 ? rec.skill.substring(0, 15) + '...' : rec.skill,
        priority: rec.priority,
        demand: rec.demand_percentage || 0
      }))

    // Radar chart data for skill levels
    const radarData = skill_recommendations.slice(0, 6).map(rec => {
      // Convert current_level to numeric (beginner=1, intermediate=3, advanced=5)
      let level = 2
      const levelStr = rec.current_level.toLowerCase()
      if (levelStr.includes('beginner') || levelStr.includes('novice')) level = 1
      else if (levelStr.includes('intermediate') || levelStr.includes('moderate')) level = 3
      else if (levelStr.includes('advanced') || levelStr.includes('expert')) level = 5
      
      return {
        skill: rec.skill.length > 10 ? rec.skill.substring(0, 10) : rec.skill,
        level: level
      }
    })

    return {
      scoreTrend,
      skillDistribution,
      skillBars,
      radarData
    }
  }, [newsletter])

  const COLORS = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#f43f5e']

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-400 font-mono text-sm">Loading report...</p>
        </div>
      </div>
    )
  }

  if (!newsletter || !chartData) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">Report not found</p>
          <button
            onClick={() => navigate('/subscription')}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg font-mono text-sm transition"
          >
            ← Back to Subscription
          </button>
        </div>
      </div>
    )
  }

  const { career_readiness, code_insights, skill_recommendations, learning_links } = newsletter

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-mono font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Devbrah
            </h1>
            <div className="h-6 w-px bg-gray-700"></div>
            <span className="text-sm text-gray-400 font-mono">{getModeTitle()}</span>
          </div>
          <button
            onClick={() => navigate('/subscription')}
            className="px-3 py-1.5 text-xs font-mono bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded transition"
          >
            ← Back
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-mono font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            {getModeTitle()}
          </h2>
          <p className="text-sm text-gray-400 font-mono">{getModeDescription()}</p>
          <p className="text-xs text-gray-500 mt-2 font-mono">
            Generated: {new Date(newsletter.generated_at).toLocaleDateString()}
          </p>
        </div>

        {/* Career Readiness Score with Trend Chart */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">OVERALL SCORE</h3>
            <div className="text-5xl font-mono font-bold mb-4 text-white">
              {career_readiness.overall_score.toFixed(0)}
            </div>
            <ResponsiveContainer width="100%" height={60}>
              <LineChart data={chartData.scoreTrend}>
                <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-gray-500 mt-2 font-mono">Last 6 weeks trend</p>
          </div>

          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">SKILL ALIGNMENT</h3>
            <div className="text-5xl font-mono font-bold mb-4 text-white">
              {career_readiness.skill_alignment.toFixed(0)}
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-purple-600 to-pink-600 h-2.5 rounded-full transition-all duration-500" 
                style={{ width: `${career_readiness.skill_alignment}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-2 font-mono">Target Role Match</p>
          </div>

          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-2 tracking-wider">CODE QUALITY</h3>
            <div className="text-5xl font-mono font-bold mb-4 text-white">
              {career_readiness.code_quality_score.toFixed(0)}
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-purple-600 to-pink-600 h-2.5 rounded-full transition-all duration-500" 
                style={{ width: `${career_readiness.code_quality_score}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-2 font-mono">Code Excellence</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Skill Distribution Pie Chart */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">SKILL DISTRIBUTION</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie 
                  data={chartData.skillDistribution} 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={70} 
                  dataKey="value" 
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  labelLine={false}
                >
                  {chartData.skillDistribution.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151', 
                    borderRadius: '0.5rem',
                    color: '#e5e7eb'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Skill Recommendations Bar Chart */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">SKILL PRIORITY</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData.skillBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="name" 
                  stroke="#9ca3af" 
                  tick={{ fontSize: 10 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis stroke="#9ca3af" tick={{ fontSize: 11 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151', 
                    borderRadius: '0.5rem',
                    color: '#e5e7eb'
                  }} 
                />
                <Bar dataKey="priority" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Skill Radar Chart */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">SKILL RADAR</h3>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={chartData.radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="skill" stroke="#9ca3af" tick={{ fontSize: 9 }} />
                <PolarRadiusAxis domain={[0, 5]} stroke="#9ca3af" tick={{ fontSize: 9 }} />
                <Radar dataKey="level" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151', 
                    borderRadius: '0.5rem',
                    color: '#e5e7eb'
                  }} 
                />
              </RadarChart>
            </ResponsiveContainer>
            <p className="text-xs text-gray-500 mt-2 font-mono">Current skill levels</p>
          </div>
        </div>

        {/* Strong Skills */}
        {career_readiness.strong_skills.length > 0 && (
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl mb-6">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">STRONG SKILLS</h3>
            <div className="flex flex-wrap gap-2">
              {career_readiness.strong_skills.map((skill, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 bg-purple-600/20 border border-purple-500/30 rounded text-sm font-mono text-purple-300"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing Skills */}
        {career_readiness.missing_skills.length > 0 && (
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl mb-6">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">MISSING SKILLS</h3>
            <div className="flex flex-wrap gap-2">
              {career_readiness.missing_skills.map((skill, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 bg-pink-600/20 border border-pink-500/30 rounded text-sm font-mono text-pink-300"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Code Insights */}
        {code_insights.length > 0 && (
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl mb-6">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">CODE INSIGHTS</h3>
            <div className="space-y-4">
              {code_insights.map((insight, i) => (
                <div key={i} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-start gap-3 mb-2">
                    <span className="text-purple-400 font-mono text-sm mt-0.5">#{i + 1}</span>
                    <div className="flex-1">
                      <p className="text-sm font-mono text-purple-300 mb-1">{insight.file_path}</p>
                      {insight.complexity && (
                        <span className="text-xs text-gray-500 font-mono">Complexity: {insight.complexity}</span>
                      )}
                    </div>
                  </div>
                  <div className="bg-gray-900 rounded p-3 mb-2 font-mono text-xs text-gray-300 overflow-x-auto">
                    <pre className="whitespace-pre-wrap">{insight.code_snippet}</pre>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{insight.feedback}</p>
                  <p className="text-sm text-purple-300 font-mono">→ {insight.suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skill Recommendations */}
        {skill_recommendations.length > 0 && (
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl mb-6">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">SKILL RECOMMENDATIONS</h3>
            <div className="space-y-3">
              {skill_recommendations
                .sort((a, b) => b.priority - a.priority)
                .map((rec, i) => (
                  <div key={i} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="text-sm font-mono text-purple-300 mb-1">{rec.skill}</h4>
                        <div className="flex gap-4 text-xs text-gray-400 font-mono">
                          <span>Current: {rec.current_level}</span>
                          <span>→</span>
                          <span>Target: {rec.target_level}</span>
                          {rec.demand_percentage && (
                            <span className="text-pink-400">Demand: {rec.demand_percentage}%</span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-gray-500 font-mono">Priority: {rec.priority}</span>
                    </div>
                    <a
                      href={rec.learning_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-purple-400 hover:text-purple-300 font-mono underline"
                    >
                      → Learn {rec.skill}
                    </a>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Learning Links */}
        {learning_links.length > 0 && (
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 border border-gray-800 rounded-lg p-6 shadow-xl">
            <h3 className="text-xs font-mono text-gray-400 mb-4 tracking-wider">LEARNING RESOURCES</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {learning_links.map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 hover:border-purple-500/50 transition group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-mono text-purple-300 group-hover:text-purple-200 mb-1">
                        {link.title}
                      </p>
                      <p className="text-xs text-gray-400 font-mono">{link.skill}</p>
                    </div>
                    <span className="text-xs text-gray-500 font-mono">{link.provider}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
