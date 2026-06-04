import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authApi } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    try { return stored ? JSON.parse(stored) : null } catch { return null }
  })
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))

  const fetchMe = useCallback(async () => {
    if (!token) { setLoading(false); return }
    try {
      const res = await authApi.getMe()
      const u = res.data
      setUser(u)
      localStorage.setItem('user', JSON.stringify(u))
    } catch {
      logout()
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { fetchMe() }, [fetchMe])

  const loginWithToken = (tok, userData) => {
    localStorage.setItem('auth_token', tok)
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(tok)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const isAuthenticated = !!token && !!user

  return (
    <AuthContext.Provider value={{ user, token, loading, isAuthenticated, loginWithToken, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
