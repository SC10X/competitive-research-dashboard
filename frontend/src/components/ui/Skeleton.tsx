import { clsx } from 'clsx'

type SkeletonVariant = 'text' | 'card' | 'table-row' | 'chart'

interface SkeletonProps {
  variant?: SkeletonVariant
  className?: string
}

function TextSkeleton() {
  return (
    <div className="space-y-3">
      <div className="h-4 w-3/4 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
      <div className="h-4 w-1/2 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
      <div className="h-4 w-5/6 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
    </div>
  )
}

function CardSkeleton() {
  return (
    <div className="rounded-xl border border-surface-200 p-5 dark:border-surface-700">
      <div className="mb-4 h-4 w-1/3 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
      <div className="mb-3 h-8 w-1/2 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
      <div className="h-4 w-1/4 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
    </div>
  )
}

function TableRowSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 rounded-lg border border-surface-200 px-4 py-3 dark:border-surface-700"
        >
          <div className="h-4 w-1/4 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
          <div className="h-4 w-1/3 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
          <div className="h-4 w-1/6 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
        </div>
      ))}
    </div>
  )
}

function ChartSkeleton() {
  return (
    <div className="flex h-64 items-end gap-2 rounded-xl border border-surface-200 p-5 dark:border-surface-700">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="flex-1 animate-pulse rounded bg-surface-200 dark:bg-surface-700"
          style={{ height: `${30 + Math.random() * 70}%` }}
        />
      ))}
    </div>
  )
}

const variantComponents: Record<SkeletonVariant, () => JSX.Element> = {
  text: TextSkeleton,
  card: CardSkeleton,
  'table-row': TableRowSkeleton,
  chart: ChartSkeleton,
}

export function Skeleton({ variant = 'text', className }: SkeletonProps) {
  const Component = variantComponents[variant]
  return (
    <div className={className} role="status" aria-label="Loading">
      <Component />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

export default Skeleton
