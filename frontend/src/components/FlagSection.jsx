import { Plus } from 'lucide-react'
import FlagRow from './FlagRow'

const EMPTY_ENTRY = () => ({ flag: '', value: '' })

export default function FlagSection({ flagOptions, entries, onChange }) {
  const rows = entries && entries.length > 0 ? entries : [EMPTY_ENTRY(), EMPTY_ENTRY(), EMPTY_ENTRY()]

  const updateEntry = (index, updated) => {
    onChange(rows.map((e, i) => (i === index ? updated : e)))
  }

  const removeEntry = (index) => {
    onChange(rows.filter((_, i) => i !== index))
  }

  const addEntry = () => {
    onChange([...rows, EMPTY_ENTRY()])
  }

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Column headers */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 px-1">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-widest">Flag</span>
        <span className="text-xs font-medium text-gray-500 uppercase tracking-widest">Value</span>
      </div>

      {/* Flag rows */}
      <div className="space-y-3">
        {rows.map((entry, index) => (
          <FlagRow
            key={index}
            flagOptions={flagOptions}
            entry={entry}
            onChange={(updated) => updateEntry(index, updated)}
            onRemove={() => removeEntry(index)}
            canRemove={rows.length > 1}
          />
        ))}
      </div>

      {/* Add more button */}
      <button
        onClick={addEntry}
        className="mt-2 flex items-center gap-2 text-sm text-brand-400 hover:text-brand-300 transition-colors duration-200 group"
      >
        <span className="w-6 h-6 rounded-md bg-brand-600/20 border border-brand-500/30 flex items-center justify-center group-hover:bg-brand-600/40 transition-colors duration-200">
          <Plus size={13} />
        </span>
        Add flag
      </button>
    </div>
  )
}
