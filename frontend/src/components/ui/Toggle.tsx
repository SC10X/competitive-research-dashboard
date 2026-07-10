import { clsx } from 'clsx'
import type { ReactNode } from 'react'

interface ToggleOption {
  value: string
  label: ReactNode
  icon?: ReactNode
}

interface ToggleProps {
  options: ToggleOption[]
  value: string
  onChange: (value: string) => void
  className?: string
}

export function Toggle({ options, value, onChange, className }: ToggleProps) {
  return (
    <div
      className={clsx(
        'inline-flex rounded-lg border border-surface-200 bg-surface-100 p-1 dark:border-surface-700 dark:bg-surface-800',
        className,
      )}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={clsx(
            'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
            value === option.value
              ? 'bg-white text-surface-900 shadow-sm dark:bg-surface-700 dark:text-surface-50'
              : 'text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-200',
          )}
        >
          {option.icon}
          {option.label}
        </button>
      ))}
    </div>
  )
}

export default Toggle
