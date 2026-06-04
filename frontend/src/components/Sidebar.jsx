import {
  Mail, Inbox, Star, Send, Trash2, Tag, PenSquare,
  LogOut, ChevronLeft, User, Sparkles,
} from 'lucide-react'

const NAV_ITEMS = [
  { id: 'INBOX', label: 'Inbox', icon: Inbox },
  { id: 'STARRED', label: 'Starred', icon: Star },
  { id: 'SENT', label: 'Sent', icon: Send },
  { id: 'TRASH', label: 'Trash', icon: Trash2 },
]

export default function Sidebar({ open, onToggle, activeLabel, onLabelChange, onCompose, onLogout, user, unreadCount }) {
  return (
    <>
      {/* Overlay for mobile */}
      {open && <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={onToggle} />}

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-30 lg:z-auto
        flex flex-col bg-dark-950 border-r border-dark-800
        transition-all duration-300 ease-in-out
        ${open ? 'w-64 translate-x-0' : 'w-0 -translate-x-full lg:w-16 lg:translate-x-0'}
      `}>
        <div className={`flex flex-col h-full overflow-hidden ${open ? 'w-64' : 'w-16'} transition-all duration-300`}>
          {/* Logo */}
          <div className="flex items-center justify-between px-4 py-5 border-b border-dark-800">
            {open && (
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center shrink-0 shadow-glow">
                  <Mail className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold text-white text-sm truncate">AI Email</span>
              </div>
            )}
            {!open && (
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto shadow-glow">
                <Mail className="w-4 h-4 text-white" />
              </div>
            )}
            {open && (
              <button onClick={onToggle} className="btn-ghost p-1.5 ml-auto">
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Compose button */}
          <div className="px-3 py-4">
            <button
              id="sidebar-compose-btn"
              onClick={onCompose}
              className={`btn-primary w-full text-sm ${!open ? 'px-0 justify-center' : ''}`}
            >
              <PenSquare className="w-4 h-4" />
              {open && 'Compose'}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                id={`nav-${id.toLowerCase()}`}
                onClick={() => onLabelChange(id)}
                className={`sidebar-link w-full ${activeLabel === id ? 'active' : ''} ${!open ? 'justify-center px-0' : ''}`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {open && (
                  <span className="flex-1 text-left truncate">{label}</span>
                )}
                {open && id === 'INBOX' && unreadCount > 0 && (
                  <span className="bg-primary-600 text-white text-xs font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                    {unreadCount}
                  </span>
                )}
              </button>
            ))}

            {open && (
              <div className="pt-4 pb-2">
                <div className="flex items-center gap-2 px-3 py-1">
                  <Tag className="w-3 h-3 text-dark-600" />
                  <span className="text-dark-600 text-xs font-medium uppercase tracking-wide">AI Features</span>
                </div>
                <div className="mt-1 px-3 py-2 glass-light rounded-lg space-y-1">
                  <p className="text-dark-500 text-xs flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-primary-500" />
                    Reply Generator
                  </p>
                  <p className="text-dark-500 text-xs flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-primary-500" />
                    Summarizer
                  </p>
                  <p className="text-dark-500 text-xs flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-primary-500" />
                    Classifier
                  </p>
                  <p className="text-dark-500 text-xs flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-primary-500" />
                    Grammar Fix
                  </p>
                </div>
              </div>
            )}
          </nav>

          {/* User profile */}
          <div className="border-t border-dark-800 p-3">
            <div className={`flex items-center gap-3 ${!open ? 'justify-center' : ''}`}>
              {user?.picture ? (
                <img src={user.picture} alt="avatar" className="w-8 h-8 rounded-full shrink-0 ring-2 ring-dark-700" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-dark-400" />
                </div>
              )}
              {open && (
                <>
                  <div className="flex-1 min-w-0">
                    <p className="text-dark-200 text-xs font-medium truncate">{user?.name || 'User'}</p>
                    <p className="text-dark-500 text-xs truncate">{user?.email}</p>
                  </div>
                  <button
                    id="logout-btn"
                    onClick={onLogout}
                    className="btn-ghost p-1.5 text-dark-500 hover:text-red-400"
                    title="Sign out"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
