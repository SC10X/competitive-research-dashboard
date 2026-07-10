import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useCompareStore } from '@/store/compareStore'
import type { Brand } from '@/types/brand'
import { PRICE_TIER_LABELS, PRICE_TIER_COLORS } from '@/types/brand'

interface CompareBasketProps {}

export default function CompareBasket(_props: CompareBasketProps) {
  const navigate = useNavigate()
  const { items, removeItem, clearAll } = useCompareStore()
  const [isOpen, setIsOpen] = useState(false)

  if (items.length === 0) {
    return (
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-4 py-3 bg-white dark:bg-surface-800 text-surface-500 dark:text-surface-400
                     rounded-full shadow-lg border border-surface-200 dark:border-surface-700
                     hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
        >
          <span className="text-sm font-medium">选择对比</span>
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-3 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-colors"
      >
        <span className="text-sm font-medium">已选 {items.length} 个品牌</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute bottom-14 right-0 w-72 bg-white dark:bg-surface-800 rounded-xl shadow-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
          <div className="p-4 border-b border-surface-100 dark:border-surface-700">
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-surface-900 dark:text-white">对比篮</h3>
              <button
                onClick={clearAll}
                className="text-xs text-surface-500 hover:text-red-600 dark:hover:text-red-400"
              >
                清空
              </button>
            </div>
            <p className="text-xs text-surface-400 mt-1">最多选择 6 个品牌</p>
          </div>
          <div className="max-h-64 overflow-y-auto p-2">
            {items.map((item) => {
              const colorClasses =
                PRICE_TIER_COLORS[(item as any).price_tier || ''] ||
                'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-700/50"
                >
                  <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-600 dark:text-primary-400 font-bold text-xs">
                      {item.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-surface-900 dark:text-white truncate">
                      {item.name}
                    </p>
                    <p className="text-[10px] text-surface-400">
                      {(item as any).price_tier
                        ? PRICE_TIER_LABELS[(item as any).price_tier] || (item as any).price_tier
                        : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="p-1.5 text-surface-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              )
            })}
          </div>
          <div className="p-3 border-t border-surface-100 dark:border-surface-700">
            <button
              onClick={() => {
                navigate(`/compare?brands=${items.map((i) => i.id).join(',')}`)
              }}
              disabled={items.length < 2}
              className="w-full py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              开始对比
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
