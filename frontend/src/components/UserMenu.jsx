import { useState, useRef, useEffect } from 'react'
import { LogOut, User, ChevronDown, Mail } from 'lucide-react'

/**
 * UserMenu — a compact, premium user-profile dropdown shown in every page header.
 * Displays the logged-in user's avatar, name and full email address.
 */
export default function UserMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  if (!user) return null

  const initials = ((user.name || user.email || 'U').trim()[0] || 'U').toUpperCase()

  return (
    <div ref={ref} className="relative">
      {/* Trigger button */}
      <button
        id="user-menu-btn"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-2 py-1.5 rounded-xl border border-dark-700 bg-dark-900 hover:border-primary-700/50 hover:bg-dark-800 transition-all duration-200 group"
        title={user.email}
      >
        {/* Avatar */}
        {user.picture ? (
          <img
            src={user.picture}
            alt={user.name || 'avatar'}
            className="w-7 h-7 rounded-full ring-2 ring-dark-700 group-hover:ring-primary-700/40 transition-all shrink-0"
          />
        ) : (
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-600 to-purple-700 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold">{initials}</span>
          </div>
        )}

        {/* Name + email — visible on md+ screens */}
        <div className="hidden md:flex flex-col items-start leading-tight min-w-0 max-w-[140px]">
          <span className="text-dark-100 text-xs font-medium truncate w-full">
            {user.name || 'User'}
          </span>
          <span className="text-dark-500 text-[10px] truncate w-full">{user.email}</span>
        </div>

        <ChevronDown
          className={`w-3.5 h-3.5 text-dark-500 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Dropdown panel */}
      {open && (
        <div className="absolute right-0 top-full mt-2 w-72 glass border border-dark-700 rounded-2xl shadow-2xl z-50 overflow-hidden animate-slide-up">
          {/* Profile header */}
          <div className="flex items-center gap-3 px-4 py-4 border-b border-dark-800 bg-dark-900/60">
            {user.picture ? (
              <img
                src={user.picture}
                alt={user.name || 'avatar'}
                className="w-11 h-11 rounded-full ring-2 ring-primary-700/40 shrink-0"
              />
            ) : (
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary-600 to-purple-700 flex items-center justify-center shrink-0">
                <span className="text-white text-base font-bold">{initials}</span>
              </div>
            )}
            <div className="flex flex-col min-w-0">
              <p className="text-dark-100 text-sm font-semibold truncate">
                {user.name || 'User'}
              </p>
              <div className="flex items-center gap-1 mt-0.5">
                <Mail className="w-3 h-3 text-primary-400 shrink-0" />
                <p className="text-primary-300 text-xs font-medium truncate">{user.email}</p>
              </div>
            </div>
          </div>

          {/* Account info row */}
          <div className="px-4 py-3">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-dark-800/60 border border-dark-700/50">
              <User className="w-3.5 h-3.5 text-dark-500 shrink-0" />
              <div className="flex flex-col min-w-0">
                <span className="text-dark-500 text-[10px] uppercase tracking-wide font-medium">
                  Signed-in account
                </span>
                <span className="text-dark-200 text-xs font-medium truncate">{user.email}</span>
              </div>
            </div>
          </div>

          {/* Sign out */}
          <div className="px-4 pb-4">
            <button
              id="user-menu-logout-btn"
              onClick={() => { setOpen(false); onLogout?.() }}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-900/20 border border-red-800/30 text-red-400 hover:bg-red-900/40 hover:text-red-300 transition-all duration-200 text-sm font-medium"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
