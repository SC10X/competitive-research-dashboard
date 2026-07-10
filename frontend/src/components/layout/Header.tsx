import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUIStore } from '@/store/uiStore'
import { useCompareStore } from '@/store/compareStore'
import Breadcrumb from './Breadcrumb'
import { Menu, Search, ShoppingBasket } from 'lucide-react'

export default function Header() {
  const { setSidebarOpen } = useUIStore()
  const items = useCompareStore((s) => s.items)
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-surface-900/80 backdrop-blur-sm border-b border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        {/* Left: hamburger + breadcrumb */}
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-600 dark:text-surface-400"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="hidden sm:block">
            <Breadcrumb />
          </div>
        </div>

        {/* Right: search + compare basket */}
        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchQuery.trim()) {
                  navigate(`/brands?search=${encodeURIComponent(searchQuery.trim())}`)
                }
              }}
              placeholder="搜索品牌..."
              className="w-56 lg:w-72 pl-9 pr-4 py-2 text-sm
                         bg-surface-100 dark:bg-surface-800
                         border border-surface-200 dark:border-surface-700
                         rounded-lg
                         text-surface-900 dark:text-white
                         placeholder:text-surface-400
                         focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500
                         transition-all"
            />
          </div>

          {/* Compare basket button */}
          <button
            onClick={() => navigate('/compare')}
            className="relative p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-600 dark:text-surface-400 transition-colors"
            title="对比篮"
          >
            <ShoppingBasket className="w-5 h-5" />
            {items.length > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-primary-600 text-white text-xs font-bold rounded-full flex items-center justify-center">
                {items.length}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
