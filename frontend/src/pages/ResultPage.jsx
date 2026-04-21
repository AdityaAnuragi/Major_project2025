import { useMemo } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Terminal, ArrowLeft, Globe, AlertTriangle,
  CheckCircle, Copy, Download, FolderTree, FileText, Network,
  ShieldAlert, Database, ListChecks, Info
} from 'lucide-react'

function buildTerminalOutput(result) {
  if (!result) return ''
  const lines = []
  lines.push(`[*] Target: ${result.target || '(unknown)'}`)
  lines.push(`[*] Server tech: ${result.server_tech || 'Unknown'}`)
  lines.push(`[*] Language: ${result.language || 'Unknown'}`)
  lines.push('')

  const queries = result.queries_executed || []
  if (queries.length) {
    lines.push(`[*] Commands executed (${queries.length}):`)
    queries.forEach((q, i) => {
      lines.push(`  ${i + 1}. ${q}`)
    })
    lines.push('')
  }

  const endpoints = result.endpoints || {}
  const totalEndpoints =
    (endpoints.directory?.length || 0) +
    (endpoints.file?.length || 0) +
    (endpoints.subdomain?.length || 0)
  lines.push(`[*] Endpoints discovered: ${totalEndpoints}`)
  for (const cat of ['directory', 'file', 'subdomain']) {
    const list = endpoints[cat] || []
    if (!list.length) continue
    lines.push(`  -- ${cat} (${list.length}) --`)
    list.forEach(u => lines.push(`  [200] ${u}`))
  }
  lines.push('')

  const xss = result.xss || { confirmed: [], potential: [] }
  lines.push(`[*] XSS — confirmed: ${xss.confirmed?.length || 0}, potential: ${xss.potential?.length || 0}`)
  ;(xss.confirmed || []).forEach(l => lines.push(`  ${l}`))
  ;(xss.potential || []).forEach(l => lines.push(`  ${l}`))
  lines.push('')

  const sqli = result.sqli || { confirmed: [], potential: [] }
  lines.push(`[*] SQLi — confirmed: ${sqli.confirmed?.length || 0}, potential: ${sqli.potential?.length || 0}`)
  ;(sqli.confirmed || []).forEach(l => lines.push(`  ${l}`))
  ;(sqli.potential || []).forEach(l => lines.push(`  ${l}`))
  lines.push('')

  lines.push('[*] Scan complete')
  return lines.join('\n')
}

const MOCK_OUTPUT = `[*] No scan result present — this is a placeholder view.
[*] Start a scan from the Setup page to see real output.`

export default function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result || null
  const targetUrl = result?.target || location.state?.url || 'https://target.example.com'

  const terminalOutput = useMemo(
    () => (result ? buildTerminalOutput(result) : MOCK_OUTPUT),
    [result]
  )

  const endpoints = result?.endpoints || { directory: [], file: [], subdomain: [] }
  const totalEndpoints =
    (endpoints.directory?.length || 0) +
    (endpoints.file?.length || 0) +
    (endpoints.subdomain?.length || 0)

  const xssConfirmed = result?.xss?.confirmed || []
  const xssPotential = result?.xss?.potential || []
  const sqliConfirmed = result?.sqli?.confirmed || []
  const sqliPotential = result?.sqli?.potential || []

  const totalFindings =
    xssConfirmed.length + xssPotential.length +
    sqliConfirmed.length + sqliPotential.length

  const commands = result?.queries_executed || []

  const stats = [
    { label: 'Endpoints', value: String(totalEndpoints), icon: Network, color: 'text-sky-400', bg: 'bg-sky-500/10 border-sky-500/20' },
    { label: 'Findings',  value: String(totalFindings),  icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { label: 'Commands',  value: String(commands.length), icon: ListChecks, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
    { label: 'Status',    value: result ? 'Done' : 'No data', icon: Globe, color: 'text-brand-400', bg: 'bg-brand-500/10 border-brand-500/20' },
  ]

  const handleCopy = () => {
    const payload = result ? JSON.stringify(result, null, 2) : terminalOutput
    navigator.clipboard.writeText(payload).catch(() => {})
  }

  const handleDownload = () => {
    const payload = result ? JSON.stringify(result, null, 2) : terminalOutput
    const blob = new Blob([payload], { type: result ? 'application/json' : 'text/plain' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = result ? 'scan_results.json' : 'scan_results.txt'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="glow-dot" />
            <span className={`text-xs font-semibold uppercase tracking-widest ${
              result ? 'text-emerald-400' : 'text-gray-500'
            }`}>
              {result ? 'Scan Complete' : 'No Scan Data'}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white">Results</h1>
          <div className="flex items-center gap-2 mt-1">
            <Globe size={13} className="text-gray-500" />
            <span className="text-gray-400 text-sm font-mono truncate max-w-xs sm:max-w-md">{targetUrl}</span>
            {result?.server_tech && (
              <span className="text-xs px-2 py-0.5 rounded-full border bg-sky-500/10 text-sky-400 border-sky-500/20">
                {result.server_tech}
              </span>
            )}
            {result?.language && (
              <span className="text-xs px-2 py-0.5 rounded-full border bg-white/5 text-gray-400 border-white/10">
                lang: {result.language}
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button onClick={() => navigate('/')} className="btn-secondary">
            <ArrowLeft size={14} />
            New Scan
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map(stat => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className={`glass-card p-4 flex items-center gap-3 border ${stat.bg}`}>
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${stat.bg}`}>
                <Icon size={16} className={stat.color} />
              </div>
              <div>
                <p className="text-gray-500 text-xs">{stat.label}</p>
                <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Empty state when no result */}
      {!result && (
        <div className="glass-card p-6 border border-white/5 flex items-start gap-3">
          <Info size={18} className="text-sky-400 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-white font-semibold mb-1">No scan results yet</h3>
            <p className="text-gray-400 text-sm">
              Head to the Setup page and click <span className="text-brand-300 font-medium">Start Scan</span> to run a scan against the backend.
            </p>
          </div>
        </div>
      )}

      {/* Findings: XSS + SQLi */}
      {result && (totalFindings > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <FindingsCard
            title="XSS (XSStrike)"
            icon={ShieldAlert}
            confirmed={xssConfirmed}
            potential={xssPotential}
            accent="red"
          />
          <FindingsCard
            title="SQLi (sqlmap)"
            icon={Database}
            confirmed={sqliConfirmed}
            potential={sqliPotential}
            accent="amber"
          />
        </div>
      )}

      {/* Endpoints */}
      {result && totalEndpoints > 0 && (
        <div className="glass-card p-5 border border-white/5">
          <div className="flex items-center gap-2 mb-4">
            <Network size={16} className="text-sky-400" />
            <h3 className="text-white font-semibold">Discovered endpoints</h3>
            <span className="text-xs text-gray-500">({totalEndpoints})</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <EndpointGroup label="Directories" icon={FolderTree} items={endpoints.directory} />
            <EndpointGroup label="Files"       icon={FileText}   items={endpoints.file} />
            <EndpointGroup label="Subdomains"  icon={Network}    items={endpoints.subdomain} />
          </div>
        </div>
      )}

      {/* Terminal output */}
      <div className="glass-card overflow-hidden border border-white/5">
        <div className="flex items-center justify-between px-5 py-3 bg-dark-800/70 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500/70" />
              <span className="w-3 h-3 rounded-full bg-amber-500/70" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/70" />
            </div>
            <div className="flex items-center gap-2">
              <Terminal size={14} className="text-gray-500" />
              <span className="text-gray-400 text-xs font-mono">scan_output.log</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-white/5 transition-all duration-200"
            >
              <Copy size={12} />
              Copy
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 text-xs text-brand-400 hover:text-brand-300 px-2.5 py-1.5 rounded-lg hover:bg-brand-500/10 transition-all duration-200"
            >
              <Download size={12} />
              Download
            </button>
          </div>
        </div>

        <div className="p-5 overflow-auto max-h-[480px]">
          <pre className="text-sm font-mono text-gray-300 leading-relaxed whitespace-pre-wrap break-words">
            {terminalOutput.split('\n').map((line, i) => {
              let cls = 'text-gray-300'
              if (line.startsWith('[*]')) cls = 'text-sky-400'
              else if (line.includes('[200]')) cls = 'text-emerald-400'
              else if (line.includes('[++]')) cls = 'text-red-400 font-medium'
              else if (line.toLowerCase().includes('potentially vulnerable')) cls = 'text-amber-400'
              else if (line.trim().startsWith('--')) cls = 'text-brand-400'
              return <span key={i} className={`block ${cls}`}>{line || ' '}</span>
            })}
          </pre>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-center gap-2 text-gray-600 text-xs pb-4">
        {result ? (
          <>
            <CheckCircle size={12} className="text-emerald-600" />
            Live results from backend
          </>
        ) : (
          <>
            <Info size={12} />
            Start a scan to populate this page
          </>
        )}
      </div>
    </main>
  )
}

function FindingsCard({ title, icon: Icon, confirmed, potential, accent }) {
  const colors = {
    red:   { border: 'border-red-500/25',   bg: 'bg-red-500/5',   text: 'text-red-300',   icon: 'text-red-400',   pot: 'text-amber-300' },
    amber: { border: 'border-amber-500/25', bg: 'bg-amber-500/5', text: 'text-amber-300', icon: 'text-amber-400', pot: 'text-amber-200' },
  }[accent]

  const hasAny = confirmed.length > 0 || potential.length > 0

  return (
    <div className={`glass-card p-5 border ${colors.border} ${colors.bg}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon size={16} className={colors.icon} />
        <h3 className={`font-semibold ${colors.text}`}>{title}</h3>
        <span className="text-xs text-gray-500 ml-auto">
          {confirmed.length} confirmed / {potential.length} potential
        </span>
      </div>
      {!hasAny && (
        <p className="text-gray-500 text-sm">Nothing flagged.</p>
      )}
      {confirmed.length > 0 && (
        <>
          <p className="text-xs uppercase tracking-wide text-gray-500 mt-1 mb-1.5">Confirmed</p>
          <ul className="space-y-1 text-xs font-mono">
            {confirmed.map((line, i) => (
              <li key={`c-${i}`} className="text-emerald-300 break-words">{line}</li>
            ))}
          </ul>
        </>
      )}
      {potential.length > 0 && (
        <>
          <p className="text-xs uppercase tracking-wide text-gray-500 mt-3 mb-1.5">Potential</p>
          <ul className="space-y-1 text-xs font-mono">
            {potential.map((line, i) => (
              <li key={`p-${i}`} className={`${colors.pot} break-words`}>{line}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

function EndpointGroup({ label, icon: Icon, items }) {
  const list = items || []
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} className="text-gray-400" />
        <span className="text-sm font-medium text-gray-200">{label}</span>
        <span className="text-xs text-gray-500">({list.length})</span>
      </div>
      {list.length === 0 ? (
        <p className="text-xs text-gray-600">None</p>
      ) : (
        <ul className="space-y-1 max-h-64 overflow-auto pr-1">
          {list.map((u, i) => (
            <li key={i} className="text-xs font-mono text-emerald-300/90 break-words">{u}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
