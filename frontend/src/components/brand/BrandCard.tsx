import { useNavigate } from 'react-router-dom'
import { useCompareStore } from '@/store/compareStore'
import type { Brand } from '@/types/brand'
import { PRICE_TIER_LABELS, PRICE_TIER_COLORS, CATEGORY_COLORS, SCENARIO_COLORS, PRODUCT_CAT_COLORS } from '@/types/brand'
import { formatNumber } from '@/utils/format'
import BrandLogo from '@/components/brand/BrandLogo'
import { Plus, Check, Globe, Users } from 'lucide-react'

interface BrandCardProps {
  brand: Brand
}

export default function BrandCard({ brand }: BrandCardProps) {
  const navigate = useNavigate()
  const { addItem, removeItem, isInBasket } = useCompareStore()
  const inBasket = isInBasket(brand.id)

  const instagramFollowers = brand.instagram_followers || 0
  const monthlyTraffic = brand.monthly_web_visits || 0

  const initial = brand.name.charAt(0).toUpperCase()
  const colorClasses =
    PRICE_TIER_COLORS[brand.price_tier || ''] ||
    'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'

  const handleToggleCompare = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (inBasket) {
      removeItem(brand.id)
    } else {
      addItem({ id: brand.id, name: brand.name, slug: brand.slug, price_tier: brand.price_tier, logo_url: brand.logo_url })
    }
  }

  const handleCardClick = () => {
    navigate(`/brands/${brand.slug}`)
  }

  return (
    <div
      onClick={handleCardClick}
      className="group bg-white dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700
                 hover:shadow-lg hover:border-primary-300 dark:hover:border-primary-700
                 transition-all duration-200 cursor-pointer overflow-hidden flex flex-col"
    >
      {/* Top section */}
      <div className="p-5 flex-1">
        {/* Avatar + name */}
        <div className="flex items-start gap-3 mb-3">
          {brand.logo_url ? (
            <BrandLogo
              name={brand.name}
              website={brand.website}
              logoUrl={brand.logo_url}
              size="md"
            />
          ) : (
            <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
              <span className="text-primary-600 dark:text-primary-400 font-bold text-lg">
                {initial}
              </span>
            </div>
          )}
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-surface-900 dark:text-white truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {brand.name}
            </h3>
            <p className="text-xs text-surface-500 dark:text-surface-400">{brand.country}</p>
          </div>
        </div>

        {/* Price tier badge */}
        {brand.price_tier && (
          <span
            className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full mb-3 ${colorClasses}`}
          >
            {PRICE_TIER_LABELS[brand.price_tier] || brand.price_tier}
          </span>
        )}

        {/* Categories */}
        {brand.categories && brand.categories.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {brand.categories.slice(0, 3).map((cat) => (
              <span
                key={cat.id}
                className={`text-xs px-1.5 py-0.5 rounded ${
                  CATEGORY_COLORS[(cat as any).category_slug || ''] ||
                  SCENARIO_COLORS[(cat as any).category_slug || ''] ||
                  PRODUCT_CAT_COLORS[(cat as any).category_slug || ''] ||
                  'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                {cat.name}
              </span>
            ))}
            {brand.categories.length > 3 && (
              <span className="text-xs text-surface-400">+{brand.categories.length - 3}</span>
            )}
          </div>
        )}

        {/* Description */}
        <p className="text-sm text-surface-500 dark:text-surface-400 line-clamp-2 leading-relaxed">
          {brand.description}
        </p>
      </div>

      {/* Bottom stats + actions */}
      <div className="px-5 py-3 border-t border-surface-100 dark:border-surface-800 bg-surface-50 dark:bg-surface-800/50">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-xs text-surface-500 dark:text-surface-400">
            {instagramFollowers > 0 && (
              <span className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5" />
                {formatNumber(instagramFollowers)}
              </span>
            )}
            {monthlyTraffic > 0 && (
              <span className="flex items-center gap-1">
                <Globe className="w-3.5 h-3.5" />
                {formatNumber(monthlyTraffic)}
              </span>
            )}
          </div>

          <button
            onClick={handleToggleCompare}
            className={`flex items-center gap-1 text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors
              ${
                inBasket
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-400'
                  : 'text-surface-500 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-700'
              }`}
          >
            {inBasket ? (
              <>
                <Check className="w-3.5 h-3.5" />
                已加入
              </>
            ) : (
              <>
                <Plus className="w-3.5 h-3.5" />
                对比
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
