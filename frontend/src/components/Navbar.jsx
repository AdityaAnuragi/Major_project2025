import { Link, useLocation } from 'react-router-dom'
import { ShieldAlert, Terminal } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-dark-800/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center shadow-lg shadow-brand-600/30 group-hover:shadow-brand-500/50 transition-shadow duration-300">
                <ShieldAlert size={18} className="text-white" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-dark-800 animate-pulse" />
            </div>
            <div>
              <span className="text-white font-bold text-lg tracking-tight">
                Pentest<span className="text-brand-400">Suite</span>
              </span>
              <p className="text-gray-500 text-xs -mt-0.5 hidden sm:block">Automated Security Scanner</p>
            </div>
          </Link>

          {/* Nav links */}
          <nav className="flex items-center gap-1">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                location.pathname === '/'
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              Setup
            </Link>
            <Link
              to="/result"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
                location.pathname === '/result'
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Terminal size={14} />
              Results
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
