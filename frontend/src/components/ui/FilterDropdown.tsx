import { clsx } from 'clsx'
import { Check, ChevronDown, Search } from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

interface FilterOption {
  value: string
  label: string
}

interface FilterDropdownProps {
  label: string
  options: FilterOption[]
  selected: string[]
  onChange: (selected: string[]) => void
  searchable?: boolean
  className?: string
}

export function FilterDropdown({
  label,
  options,
  selected,
  onChange,
  searchable = false,
  className,
}: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  const filteredOptions = useMemo(() => {
    if (!searchTerm) return options
    const term = searchTerm.toLowerCase()
    return options.filter((opt) => opt.label.toLowerCase().includes(term))
  }, [options, searchTerm])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleOption = useCallback(
    (value: string) => {
      const next = selected.includes(value)
        ? selected.filter((v) => v !== value)
        : [...selected, value]
      onChange(next)
    },
    [selected, onChange],
  )

  const clearAll = useCallback(() => {
    onChange([])
  }, [onChange])

  return (
    <div ref={containerRef} className={clsx('relative', className)}>
      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        className={clsx(
          'flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors',
          selected.length > 0
            ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
            : 'border-surface-200 bg-white text-surface-600 hover:bg-surface-50 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-400 dark:hover:bg-surface-800',
        )}
      >
        <span>{label}</span>
        {selected.length > 0 && (
          <span className="rounded-full bg-primary-600 px-1.5 py-0.5 text-xs text-white dark:bg-primary-500">
            {selected.length}
          </span>
        )}
        <ChevronDown
          className={clsx(
            'h-4 w-4 transition-transform',
            isOpen && 'rotate-180',
          )}
        />
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full z-20 mt-1 w-56 rounded-lg border border-surface-200 bg-white shadow-lg dark:border-surface-700 dark:bg-surface-900">
          {searchable && (
            <div className="border-b border-surface-200 p-2 dark:border-surface-700">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="搜索选项..."
                  className="w-full rounded-md border border-surface-200 bg-surface-50 py-1.5 pl-8 pr-2 text-sm text-surface-900 placeholder:text-surface-400 focus:border-primary-500 focus:outline-none dark:border-surface-700 dark:bg-surface-800 dark:text-surface-50"
                />
              </div>
            </div>
          )}

          {selected.length > 0 && (
            <div className="border-b border-surface-200 px-3 py-2 dark:border-surface-700">
              <button
                type="button"
                onClick={clearAll}
                className="text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400"
              >
                清除全部 ({selected.length})
              </button>
            </div>
          )}

          <div className="max-h-60 overflow-y-auto py-1">
            {filteredOptions.length === 0 ? (
              <p className="px-3 py-2 text-sm text-surface-400">无匹配选项</p>
            ) : (
              filteredOptions.map((option) => {
                const isSelected = selected.includes(option.value)
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => toggleOption(option.value)}
                    className={clsx(
                      'flex w-full items-center gap-2 px-3 py-2 text-sm transition-colors',
                      isSelected
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
                        : 'text-surface-700 hover:bg-surface-50 dark:text-surface-300 dark:hover:bg-surface-800',
                    )}
                  >
                    <span
                      className={clsx(
                        'flex h-4 w-4 shrink-0 items-center justify-center rounded border transition-colors',
                        isSelected
                          ? 'border-primary-600 bg-primary-600 dark:border-primary-500 dark:bg-primary-500'
                          : 'border-surface-300 dark:border-surface-600',
                      )}
                    >
                      {isSelected && <Check className="h-3 w-3 text-white" />}
                    </span>
                    {option.label}
                  </button>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FilterDropdown
