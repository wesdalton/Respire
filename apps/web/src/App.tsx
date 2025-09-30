import { useState, useEffect } from 'react'
import { Activity, Heart, Zap } from 'lucide-react'
import './App.css'

interface HealthCheck {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

function App() {
  const [apiStatus, setApiStatus] = useState<HealthCheck | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check if API is running
    fetch('http://localhost:8000')
      .then(res => res.json())
      .then(data => {
        setApiStatus(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Activity className="w-12 h-12 text-blue-600" />
            <h1 className="text-5xl font-bold text-gray-900">Respire</h1>
          </div>
          <p className="text-xl text-gray-600">
            AI-Powered Burnout Prevention Platform
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Built by Wes Dalton • UPenn '26
          </p>
        </div>

        {/* Status Cards */}
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Frontend</h3>
                <p className="text-sm text-gray-600">React + TypeScript</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-green-600 font-medium">Running</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-green-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Backend</h3>
                <p className="text-sm text-gray-600">FastAPI + Python</p>
              </div>
            </div>
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-yellow-600 font-medium">Connecting...</span>
              </div>
            ) : error ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className="text-sm text-red-600 font-medium">Offline</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600 font-medium">Connected</span>
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-purple-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Database</h3>
                <p className="text-sm text-gray-600">Supabase</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-yellow-600 font-medium">Pending Setup</span>
            </div>
          </div>
        </div>

        {/* API Info */}
        {apiStatus && (
          <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">API Connection Successful!</h2>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Service:</span>
                <span className="font-semibold text-gray-900">{apiStatus.service}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Version:</span>
                <span className="font-semibold text-gray-900">{apiStatus.version}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Status:</span>
                <span className="font-semibold text-green-600">{apiStatus.status}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Last Check:</span>
                <span className="text-sm text-gray-500">{new Date(apiStatus.timestamp).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-4xl mx-auto bg-red-50 border-2 border-red-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Backend Not Running</h3>
            <p className="text-red-700 mb-4">
              Make sure the FastAPI backend is running on port 8000:
            </p>
            <code className="bg-red-100 text-red-900 px-4 py-2 rounded block">
              cd apps/api && uvicorn main:app --reload
            </code>
          </div>
        )}

        {/* Next Steps */}
        <div className="max-w-4xl mx-auto mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Next Steps</h2>
          <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Set up Supabase</h3>
                <p className="text-gray-600 text-sm">Create project, configure database, set up authentication</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Deploy to Railway</h3>
                <p className="text-gray-600 text-sm">Connect GitHub repo, configure environment variables</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Deploy to Vercel</h3>
                <p className="text-gray-600 text-sm">Deploy frontend with automatic HTTPS and CDN</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">4</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Implement WHOOP OAuth</h3>
                <p className="text-gray-600 text-sm">Complete OAuth 2.0 flow with WHOOP API v2</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
