import { useNavigate } from 'react-router-dom'
import { Instagram } from 'lucide-react'
import type { Brand } from '@/types/brand'
import { PRICE_TIER_LABELS, PRICE_TIER_COLORS } from '@/types/brand'

interface BrandCardMiniProps {
  brand: Brand
}

export default function BrandCardMini({ brand }: BrandCardMiniProps) {
  const navigate = useNavigate()
  const initial = brand.name.charAt(0).toUpperCase()
  const colorClasses =
    PRICE_TIER_COLORS[brand.price_tier || ''] ||
    'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'

  return (
    <div
      onClick={() => navigate(`/brands/${brand.slug}`)}
      className="group flex items-center gap-3 p-3 bg-white dark:bg-surface-900
                 rounded-lg border border-surface-200 dark:border-surface-700
                 hover:shadow-md hover:border-primary-300 dark:hover:border-primary-700
                 transition-all duration-200 cursor-pointer"
    >
      {/* Avatar */}
      {brand.logo_url ? (
        <img
          src={brand.logo_url}
          alt={brand.name}
          className="w-10 h-10 rounded-lg object-cover flex-shrink-0"
        />
      ) : (
        <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
          <span className="text-primary-600 dark:text-primary-400 font-bold text-sm">
            {initial}
          </span>
        </div>
      )}

      {/* Info */}
      <div className="min-w-0 flex-1">
        <h4 className="font-medium text-sm text-surface-900 dark:text-white truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {brand.name}
        </h4>
        <div className="flex items-center gap-1.5 mt-1">
          {brand.price_tier && (
            <span className={`inline-block text-[10px] font-medium px-1.5 py-0.5 rounded-full ${colorClasses}`}>
              {PRICE_TIER_LABELS[brand.price_tier] || brand.price_tier}
            </span>
          )}
          {brand.instagram_url && (
            <a
              href={brand.instagram_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-surface-400 hover:text-pink-500 dark:text-surface-500 dark:hover:text-pink-400 transition-colors"
              title="Instagram"
            >
              <Instagram className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
