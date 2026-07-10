import { clsx } from 'clsx'
import { useCallback, type ReactNode } from 'react'

export interface Tab {
  key: string
  label: ReactNode
  content?: ReactNode
}

interface TabsProps {
  tabs: Tab[]
  activeKey: string
  onChange: (key: string) => void
  className?: string
}

export function Tabs({ tabs, activeKey, onChange, className }: TabsProps) {
  const handleClick = useCallback(
    (key: string) => {
      if (key !== activeKey) {
        onChange(key)
      }
    },
    [activeKey, onChange],
  )

  return (
    <div className={className}>
      <div className="flex border-b border-surface-200 dark:border-surface-700">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => handleClick(tab.key)}
            className={clsx(
              'relative px-4 py-2.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-surface-900',
              activeKey === tab.key
                ? 'text-primary-600 dark:text-primary-400'
                : 'text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-200',
            )}
          >
            {tab.label}
            {activeKey === tab.key && (
              <span className="absolute inset-x-0 bottom-0 h-0.5 bg-primary-600 dark:bg-primary-400" />
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

export default Tabs
