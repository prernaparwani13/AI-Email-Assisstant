import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Mail, Search, RefreshCw, PenSquare, X,
} from 'lucide-react'
import { emailApi } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import Sidebar from '../components/Sidebar'
import EmailList from '../components/EmailList'
import UserMenu from '../components/UserMenu'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [nextPageToken, setNextPageToken] = useState(null)
  const [totalCount, setTotalCount] = useState(0)
  const [activeLabel, setActiveLabel] = useState('INBOX')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const fetchEmails = useCallback(async (label = 'INBOX', pageToken = null) => {
    setLoading(true)
    setError(null)
    try {
      const res = await emailApi.getInbox({
        max_results: 30,
        label,                              // ← was silently dropped before
        page_token: pageToken || undefined,
      })
      setEmails(res.data.emails || [])
      setNextPageToken(res.data.next_page_token || null)
      setTotalCount(res.data.total || 0)
    } catch (err) {
      setError('Failed to load emails. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchEmails(activeLabel) }, [activeLabel])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) { fetchEmails(activeLabel); return }
    setSearching(true)
    setError(null)
    try {
      const res = await emailApi.searchEmails(searchQuery)
      setEmails(res.data.emails || [])
      setTotalCount(res.data.total || 0)
      setNextPageToken(null)
    } catch {
      setError('Search failed.')
    } finally {
      setSearching(false)
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    fetchEmails(activeLabel)
  }

  const unreadCount = emails.filter(e => !e.is_read).length

  return (
    <div className="min-h-screen bg-dark-950 flex">
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        activeLabel={activeLabel}
        onLabelChange={(l) => { setActiveLabel(l); setSearchQuery('') }}
        onCompose={() => navigate('/compose')}
        onLogout={logout}
        user={user}
        unreadCount={unreadCount}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="flex items-center gap-3 px-6 py-4 border-b border-dark-800 bg-dark-950/80 backdrop-blur sticky top-0 z-10">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="btn-ghost p-2 lg:hidden"
          >
            <Mail className="w-5 h-5" />
          </button>

          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1 max-w-xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500 pointer-events-none" />
              <input
                id="email-search-input"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search emails…"
                className="input-field pl-10 pr-10 py-2 text-sm h-9"
              />
              {searchQuery && (
                <button type="button" onClick={handleClearSearch}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </form>

          <div className="flex items-center gap-2 ml-auto">
            <button
              id="refresh-btn"
              onClick={() => fetchEmails(activeLabel)}
              disabled={loading}
              className="btn-ghost p-2"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              id="compose-header-btn"
              onClick={() => navigate('/compose')}
              className="btn-primary text-sm px-4 py-2 hidden sm:flex"
            >
              <PenSquare className="w-4 h-4" />
              Compose
            </button>
            <UserMenu user={user} onLogout={logout} />
          </div>
        </header>

        {/* Email list area */}
        <main className="flex-1 overflow-auto">
          {/* Stats bar */}
          <div className="flex items-center gap-4 px-6 py-3 border-b border-dark-800/50 text-xs text-dark-500">
            <span>{searching ? 'Searching…' : `${emails.length} emails`}</span>
            {unreadCount > 0 && (
              <span className="text-primary-400 font-medium">{unreadCount} unread</span>
            )}
            {searchQuery && (
              <span className="text-dark-400">Results for: <span className="text-dark-200">"{searchQuery}"</span></span>
            )}
          </div>

          <EmailList
            emails={emails}
            loading={loading || searching}
            error={error}
            onEmailClick={(id) => navigate(`/email/${id}`)}
            onRefresh={() => fetchEmails(activeLabel)}
          />

          {/* Load more */}
          {nextPageToken && !loading && (
            <div className="flex justify-center py-6">
              <button
                onClick={() => fetchEmails(activeLabel, nextPageToken)}
                className="btn-secondary text-sm"
              >
                Load more emails
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
