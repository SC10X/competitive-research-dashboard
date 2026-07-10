import { clsx } from 'clsx'
import { TrendingDown, TrendingUp } from 'lucide-react'
import type { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  trend?: {
    value: number
    isPositive: boolean
  }
  icon?: ReactNode
  className?: string
}

export function StatCard({ title, value, trend, icon, className }: StatCardProps) {
  return (
    <div
      className={clsx(
        'flex items-start gap-4 rounded-xl border border-surface-200 bg-white p-5 dark:border-surface-700 dark:bg-surface-900',
        className,
      )}
    >
      {icon && (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400">
          {icon}
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-sm text-surface-500 dark:text-surface-400">{title}</p>
        <p className="mt-1 text-2xl font-semibold text-surface-900 dark:text-surface-50">
          {value}
        </p>
        {trend && (
          <div className="mt-1.5 flex items-center gap-1">
            {trend.isPositive ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            <span
              className={clsx(
                'text-sm font-medium',
                trend.isPositive
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400',
              )}
            >
              {trend.value > 0 && '+'}
              {trend.value}%
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default StatCard
