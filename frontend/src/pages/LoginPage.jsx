import { useState } from 'react'
import { Mail, Zap, Shield, Sparkles, ArrowRight, Star } from 'lucide-react'
import { authApi } from '../lib/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const features = [
  { icon: Zap, label: 'AI Reply Generator', desc: 'Instant, tone-perfect replies powered by Gemini' },
  { icon: Sparkles, label: 'Smart Summarizer', desc: 'Get the gist of any email in seconds' },
  { icon: Shield, label: 'Email Classifier', desc: 'Auto-categorize emails as Work, Finance, Social…' },
  { icon: Mail, label: 'Grammar Corrector', desc: 'Polish your writing before you send' },
]

export default function LoginPage() {
  const [loading, setLoading] = useState(false)

  const handleGoogleLogin = async () => {
    setLoading(true)
    try {
      const res = await authApi.getLoginUrl()
      window.location.href = res.data.auth_url
    } catch (err) {
      console.error(err)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-950 bg-mesh flex">
      {/* Left panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 border-r border-dark-800/50">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-glow">
            <Mail className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-white">AI Email Assistant</span>
        </div>

        {/* Hero text */}
        <div className="space-y-8">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary-900/30 border border-primary-700/30 rounded-full text-primary-400 text-xs font-medium">
              <Star className="w-3 h-3" /> Powered by Google Gemini
            </div>
            <h1 className="text-5xl font-bold leading-tight">
              Your inbox,{' '}
              <span className="text-gradient">supercharged</span>{' '}
              with AI
            </h1>
            <p className="text-dark-400 text-lg leading-relaxed">
              Manage Gmail smarter. Generate replies, summarize threads, classify emails, and correct grammar — all in one place.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {features.map(({ icon: Icon, label, desc }) => (
              <div key={label} className="glass rounded-xl p-4 space-y-2 hover:border-primary-700/30 transition-colors">
                <div className="w-8 h-8 bg-primary-900/50 rounded-lg flex items-center justify-center">
                  <Icon className="w-4 h-4 text-primary-400" />
                </div>
                <p className="text-dark-100 text-sm font-medium">{label}</p>
                <p className="text-dark-500 text-xs">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        <p className="text-dark-600 text-xs">© 2025 AI Email Assistant. Built with FastAPI + Gemini.</p>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {/* Mobile logo */}
        <div className="flex lg:hidden items-center gap-3 mb-12">
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-glow">
            <Mail className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-white">AI Email Assistant</span>
        </div>

        <div className="w-full max-w-sm space-y-8 animate-slide-up">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-white">Welcome back</h2>
            <p className="text-dark-400">Sign in with your Google account to continue</p>
          </div>

          {/* Google sign-in card */}
          <div className="glass rounded-2xl p-8 space-y-6">
            <button
              id="google-login-btn"
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 py-3 px-6 bg-white hover:bg-gray-50 text-gray-900 font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
              )}
              {loading ? 'Redirecting to Google…' : 'Continue with Google'}
              {!loading && <ArrowRight className="w-4 h-4 ml-auto opacity-50 group-hover:opacity-100 transition-opacity" />}
            </button>

            <div className="text-center">
              <p className="text-dark-500 text-xs">
                We request Gmail read & send permissions only.<br />
                Your data stays secure and private.
              </p>
            </div>
          </div>

          {/* Trust badges */}
          <div className="flex items-center justify-center gap-6 text-dark-600 text-xs">
            <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> OAuth 2.0</span>
            <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> JWT Secured</span>
            <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> No Password</span>
          </div>
        </div>
      </div>
    </div>
  )
}
