import { useState } from 'react'
import { ChevronDown, X } from 'lucide-react'

export default function FlagRow({ flagOptions, entry, onChange, onRemove, canRemove }) {
  const [open, setOpen] = useState(false)
  const selectedFlag = flagOptions.find(f => f.value === entry.flag)

  return (
    <div className="flag-row group">
      {/* Flag selector */}
      <div className="relative">
        <div
          className="select-field flex items-center justify-between cursor-pointer"
          onClick={() => setOpen(o => !o)}
        >
          <span className={selectedFlag ? 'text-brand-300 font-mono' : 'text-gray-500'}>
            {selectedFlag ? selectedFlag.label : 'Select a flag…'}
          </span>
          <ChevronDown
            size={16}
            className={`text-gray-500 transition-transform duration-200 flex-shrink-0 ${open ? 'rotate-180' : ''}`}
          />
        </div>

        {/* Dropdown */}
        {open && (
          <div className="absolute z-30 mt-1 w-full bg-dark-600 border border-white/10 rounded-xl shadow-xl overflow-hidden animate-fade-in max-h-64 overflow-y-auto">
            {flagOptions.map(flag => (
              <button
                key={flag.value}
                className={`w-full text-left px-4 py-2.5 flex items-start gap-3 hover:bg-brand-600/20 transition-colors duration-150 ${
                  entry.flag === flag.value ? 'bg-brand-600/20 text-brand-300' : 'text-gray-300'
                }`}
                onClick={() => {
                  onChange({ flag: flag.value, value: '' })
                  setOpen(false)
                }}
              >
                <span className="font-mono text-brand-400 text-sm min-w-fit">{flag.label}</span>
                <span className="text-gray-500 text-xs leading-relaxed mt-0.5">{flag.description}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Value input + remove */}
      <div className="flex gap-2">
        <input
          type="text"
          className={`input-field flex-1 ${!selectedFlag || !selectedFlag.hasValue ? 'opacity-40 cursor-not-allowed' : ''}`}
          placeholder={selectedFlag?.hasValue ? (selectedFlag.placeholder || 'Enter value…') : 'No value required'}
          disabled={!selectedFlag || !selectedFlag.hasValue}
          value={entry.value}
          onChange={e => onChange({ ...entry, value: e.target.value })}
        />
        {canRemove && (
          <button
            onClick={onRemove}
            className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-dark-600 border border-white/10 text-gray-500 hover:text-red-400 hover:border-red-400/30 transition-all duration-200"
          >
            <X size={15} />
          </button>
        )}
      </div>
    </div>
  )
}
