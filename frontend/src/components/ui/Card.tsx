import { clsx } from 'clsx'
import type { HTMLAttributes, ReactNode } from 'react'

type CardPadding = 'none' | 'sm' | 'md' | 'lg'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  padding?: CardPadding
  children: ReactNode
}

const paddingStyles: Record<CardPadding, string> = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-7',
}

export function Card({
  hover = false,
  padding = 'md',
  children,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-surface-200 bg-white dark:border-surface-700 dark:bg-surface-900',
        hover &&
          'transition-shadow hover:shadow-md dark:hover:shadow-surface-950/50',
        paddingStyles[padding],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export default Card
