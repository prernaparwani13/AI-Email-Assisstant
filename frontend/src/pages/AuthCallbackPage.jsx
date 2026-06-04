import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../lib/api'

export default function AuthCallbackPage() {
  const [params] = useSearchParams()
  const { loginWithToken } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const token = params.get('token')
    if (!token) { navigate('/login'); return }

    // Store token then fetch user profile
    localStorage.setItem('auth_token', token)
    authApi.getMe()
      .then((res) => {
        loginWithToken(token, res.data)
        navigate('/dashboard', { replace: true })
      })
      .catch(() => {
        localStorage.removeItem('auth_token')
        navigate('/login')
      })
  }, [])

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-dark-300 text-sm">Signing you in…</p>
      </div>
    </div>
  )
}
