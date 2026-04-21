import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, Play, ChevronRight, Globe, AlertTriangle, Shield,
  Layers, RefreshCw, Sliders
} from 'lucide-react'
import FlagSection from '../components/FlagSection'
import {
  COMMON_FLAGS, FFUF_FLAGS, SQLMAP_FLAGS, XSSTRIKE_FLAGS
} from '../data/flags'
import { runScan } from '../api'

const TABS = [
  { id: 'common', label: 'Common', icon: Layers, flags: COMMON_FLAGS, color: 'text-sky-400', accent: 'from-sky-600/20 to-sky-500/5', border: 'border-sky-500/30' },
  { id: 'ffuf',   label: 'FFUF',   icon: Globe,  flags: FFUF_FLAGS,   color: 'text-emerald-400', accent: 'from-emerald-600/20 to-emerald-500/5', border: 'border-emerald-500/30' },
  { id: 'sqlmap', label: 'SQLMap', icon: AlertTriangle, flags: SQLMAP_FLAGS, color: 'text-amber-400', accent: 'from-amber-600/20 to-amber-500/5', border: 'border-amber-500/30' },
  { id: 'xsstrike', label: 'XSStrike', icon: Shield, flags: XSSTRIKE_FLAGS, color: 'text-red-400', accent: 'from-red-600/20 to-red-500/5', border: 'border-red-500/30' },
]

const TOOL_BADGES = {
  common: { label: 'All Tools', bg: 'bg-sky-500/10 text-sky-400 border-sky-500/20' },
  ffuf:   { label: 'Fuzzer',    bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
  sqlmap: { label: 'SQL Injection', bg: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  xsstrike: { label: 'XSS Scanner', bg: 'bg-red-500/10 text-red-400 border-red-500/20' },
}

const EMPTY_ENTRY = () => ({ flag: '', value: '' })
const INITIAL_ENTRIES = () => ({
  common:   [EMPTY_ENTRY(), EMPTY_ENTRY(), EMPTY_ENTRY()],
  ffuf:     [EMPTY_ENTRY(), EMPTY_ENTRY(), EMPTY_ENTRY()],
  sqlmap:   [EMPTY_ENTRY(), EMPTY_ENTRY(), EMPTY_ENTRY()],
  xsstrike: [EMPTY_ENTRY(), EMPTY_ENTRY(), EMPTY_ENTRY()],
})

const PHASES = [
  { key: 'run_dir_fuzz',       label: 'Directory fuzz', hint: 'ffuf directory discovery' },
  { key: 'run_file_fuzz',      label: 'File fuzz',      hint: 'ffuf file discovery' },
  { key: 'run_subdomain_fuzz', label: 'Subdomain fuzz', hint: 'ffuf subdomain discovery' },
  { key: 'run_xss',            label: 'XSS scan',       hint: 'XSStrike' },
  { key: 'run_sqli',           label: 'SQLi scan',      hint: 'sqlmap' },
]

function buildPayload(rawUrl, phases, entries) {
  const url = rawUrl.trim().replace(/^https?:\/\//i, '').replace(/\/+$/, '')
  const payload = { url, ...phases }
  const headers = []

  for (const e of entries.common || []) {
    if (!e.flag || !e.value) continue
    if (e.flag === 'threads') payload.threads = parseInt(e.value, 10)
    else if (e.flag === 'cookies') payload.cookie = e.value
    else if (e.flag === 'headers') headers.push(e.value)
  }
  for (const e of entries.ffuf || []) {
    if (!e.flag || !e.value) continue
    if (e.flag === 'rate') payload.rate = parseInt(e.value, 10)
    else if (e.flag === 'H') headers.push(e.value)
    else if (e.flag === 'threads' && payload.threads === undefined) payload.threads = parseInt(e.value, 10)
  }

  if (headers.length > 0) payload.headers = headers
  return payload
}

export default function HomePage() {
  const [url, setUrl] = useState('')
  const [activeTab, setActiveTab] = useState('common')
  const [urlError, setUrlError] = useState('')
  const [flagEntries, setFlagEntries] = useState(INITIAL_ENTRIES)
  const [phases, setPhases] = useState({
    quick: true,
    run_dir_fuzz: true,
    run_file_fuzz: false,
    run_subdomain_fuzz: false,
    run_xss: true,
    run_sqli: false,
  })
  const [isScanning, setIsScanning] = useState(false)
  const [scanError, setScanError] = useState('')
  const navigate = useNavigate()

  const currentTab = TABS.find(t => t.id === activeTab)

  const validateUrl = (val) => {
    if (!val) return 'Target URL is required'
    try { new URL(/^https?:\/\//i.test(val) ? val : `http://${val}`); return '' }
    catch { return 'Please enter a valid URL' }
  }

  const togglePhase = (key) => setPhases(p => ({ ...p, [key]: !p[key] }))
  const setTabEntries = (tabId, next) => setFlagEntries(prev => ({ ...prev, [tabId]: next }))

  const handleStart = async () => {
    const err = validateUrl(url)
    setUrlError(err)
    if (err) return

    const payload = buildPayload(url, phases, flagEntries)
    setScanError('')
    setIsScanning(true)
    try {
      const result = await runScan(payload)
      navigate('/result', { state: { url, result, payload } })
    } catch (e) {
      setScanError(e.message || 'Scan failed')
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

      {/* Hero header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="glow-dot" />
          <span className="text-brand-400 text-xs font-semibold uppercase tracking-widest">Security Scanner</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
          Configure your scan
        </h1>
        <p className="text-gray-400 text-base">
          Enter the target URL and configure tool flags to start an automated security assessment.
        </p>
      </div>

      {/* ─── Section 1: Target URL ─── */}
      <section className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/20 flex items-center justify-center">
            <Search size={15} className="text-brand-400" />
          </div>
          <div>
            <h2 className="text-white font-semibold text-lg">Target URL</h2>
            <p className="text-gray-500 text-xs">Enter the full URL of the target to scan</p>
          </div>
        </div>

        <div className="relative">
          <div className={`flex items-center bg-dark-600 border rounded-xl overflow-hidden transition-all duration-200 ${
            urlError ? 'border-red-500/60 ring-1 ring-red-500/30' : 'border-white/10 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500/30'
          }`}>
            <div className="pl-4 pr-2 text-gray-500 flex-shrink-0">
              <Globe size={16} />
            </div>
            <input
              type="url"
              value={url}
              onChange={e => { setUrl(e.target.value); setUrlError('') }}
              placeholder="https://target.example.com"
              className="flex-1 bg-transparent py-3.5 pr-4 text-gray-100 placeholder-gray-500 focus:outline-none text-sm font-mono"
            />
            {url && (
              <div className="pr-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              </div>
            )}
          </div>

          {urlError && (
            <p className="mt-2 text-xs text-red-400 flex items-center gap-1.5 animate-fade-in">
              <AlertTriangle size={12} />
              {urlError}
            </p>
          )}
        </div>
      </section>

      {/* ─── Section 2: Scan Phases ─── */}
      <section className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/20 flex items-center justify-center">
            <Sliders size={15} className="text-brand-400" />
          </div>
          <div>
            <h2 className="text-white font-semibold text-lg">Scan Phases</h2>
            <p className="text-gray-500 text-xs">Choose which tools the backend will run</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {PHASES.map(p => {
            const active = phases[p.key]
            return (
              <button
                key={p.key}
                type="button"
                onClick={() => togglePhase(p.key)}
                className={`flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-200 text-left ${
                  active
                    ? 'bg-brand-600/15 border-brand-500/40 text-white'
                    : 'bg-dark-600/60 border-white/10 text-gray-400 hover:text-white hover:border-white/20'
                }`}
              >
                <div>
                  <p className="text-sm font-medium">{p.label}</p>
                  <p className="text-xs text-gray-500">{p.hint}</p>
                </div>
                <span className={`w-9 h-5 rounded-full relative transition-colors duration-200 flex-shrink-0 ${
                  active ? 'bg-brand-500' : 'bg-dark-500'
                }`}>
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all duration-200 ${
                    active ? 'left-4' : 'left-0.5'
                  }`} />
                </span>
              </button>
            )
          })}

          <label className="flex items-center justify-between px-4 py-3 rounded-xl border bg-dark-600/60 border-white/10 cursor-pointer hover:border-white/20 transition-all duration-200">
            <div>
              <p className="text-sm font-medium text-white">Quick mode</p>
              <p className="text-xs text-gray-500">Smaller wordlists, faster</p>
            </div>
            <span
              onClick={() => togglePhase('quick')}
              className={`w-9 h-5 rounded-full relative transition-colors duration-200 flex-shrink-0 ${
                phases.quick ? 'bg-brand-500' : 'bg-dark-500'
              }`}
            >
              <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all duration-200 ${
                phases.quick ? 'left-4' : 'left-0.5'
              }`} />
            </span>
          </label>
        </div>
      </section>

      {/* ─── Section 3: Flags ─── */}
      <section className="glass-card p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/20 flex items-center justify-center">
            <Layers size={15} className="text-brand-400" />
          </div>
          <div>
            <h2 className="text-white font-semibold text-lg">Flags</h2>
            <p className="text-gray-500 text-xs">
              Recognized fields map to the backend: <span className="font-mono text-brand-300">--threads</span>, <span className="font-mono text-brand-300">--cookies</span>, <span className="font-mono text-brand-300">--headers</span>, <span className="font-mono text-brand-300">-rate</span>, <span className="font-mono text-brand-300">-H</span>.
            </p>
          </div>
        </div>

        {/* Tab bar */}
        <div className="flex flex-wrap gap-2 p-1 bg-dark-800/60 rounded-xl border border-white/5">
          {TABS.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn flex items-center gap-2 flex-1 sm:flex-none justify-center sm:justify-start ${
                  isActive ? 'tab-btn-active' : 'tab-btn-inactive'
                }`}
              >
                <Icon size={14} className={isActive ? 'text-white' : tab.color} />
                {tab.label}
                {isActive && (
                  <span className={`hidden sm:inline-flex text-xs px-2 py-0.5 rounded-full border ${TOOL_BADGES[tab.id].bg}`}>
                    {TOOL_BADGES[tab.id].label}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Active tab hint + content */}
        <div className={`bg-gradient-to-br ${currentTab.accent} border ${currentTab.border} rounded-xl p-5 space-y-4 transition-all duration-300`}>
          <div className="flex items-center justify-between">
            <p className={`text-xs font-medium ${currentTab.color}`}>
              {currentTab.label === 'Common' ? 'Flags applied to all tools' : `Flags specific to ${currentTab.label}`}
            </p>
            <span className="text-xs text-gray-600">
              Select a flag from the dropdown, then enter a value
            </span>
          </div>
          <FlagSection
            flagOptions={currentTab.flags}
            entries={flagEntries[activeTab]}
            onChange={(next) => setTabEntries(activeTab, next)}
          />
        </div>
      </section>

      {/* ─── Error banner ─── */}
      {scanError && (
        <div className="glass-card p-4 border border-red-500/30 bg-red-500/5 flex items-start gap-3">
          <AlertTriangle size={18} className="text-red-400 mt-0.5 flex-shrink-0" />
          <div className="min-w-0">
            <p className="text-red-300 font-semibold text-sm">Scan failed</p>
            <p className="text-red-200/80 text-xs break-words font-mono mt-1">{scanError}</p>
            <p className="text-gray-500 text-xs mt-2">
              Is the backend running on <span className="font-mono">http://localhost:5000</span>? Start it with <span className="font-mono">python main.py</span> in the backend directory.
            </p>
          </div>
        </div>
      )}

      {/* ─── Start Button ─── */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <p className="text-gray-500 text-sm order-2 sm:order-1">
          {isScanning
            ? 'Scan running — this may take several minutes. Please keep this tab open.'
            : 'Ensure you have permission to scan the target before proceeding.'}
        </p>
        <button
          onClick={handleStart}
          disabled={isScanning}
          className={`btn-primary w-full sm:w-auto order-1 sm:order-2 justify-center text-base py-3.5 px-8 ${
            isScanning ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          {isScanning ? (
            <>
              <RefreshCw size={16} className="animate-spin" />
              Scanning…
            </>
          ) : (
            <>
              <Play size={16} className="fill-current" />
              Start Scan
              <ChevronRight size={16} />
            </>
          )}
        </button>
      </div>
    </main>
  )
}
