const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export async function runScan(payload) {
  const res = await fetch(`${API_BASE_URL}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload ?? {}),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Scan failed (${res.status} ${res.statusText})${text ? `: ${text}` : ''}`)
  }
  return res.json()
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE_URL}/`)
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`)
  return res.json()
}

export { API_BASE_URL }
