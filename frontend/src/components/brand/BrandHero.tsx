import type { BrandDetail } from '@/types/brand'
import { PRICE_TIER_LABELS, PRICE_TIER_COLORS } from '@/types/brand'
import { useCompareStore } from '@/store/compareStore'
import { Plus, Check, Globe, ExternalLink, Calendar, ShoppingBag } from 'lucide-react'
import { Instagram } from 'lucide-react'
import { Youtube } from 'lucide-react'
import { ShoppingCart } from 'lucide-react'

interface BrandHeroProps {
  brand: BrandDetail
}

export default function BrandHero({ brand }: BrandHeroProps) {
  const { addItem, removeItem, isInBasket } = useCompareStore()
  const inBasket = isInBasket(brand.id)

  const initial = brand.name.charAt(0).toUpperCase()
  const price_tier = brand.positioning?.price_tier
  const colorClasses =
    PRICE_TIER_COLORS[price_tier || ''] ||
    'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'

  const handleToggleCompare = () => {
    if (inBasket) {
      removeItem(brand.id)
    } else {
      addItem({ id: brand.id, name: brand.name, slug: brand.slug, price_tier: brand.positioning?.price_tier, logo_url: brand.logo_url })
    }
  }

  return (
    <div className="bg-white dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 overflow-hidden">
      <div className="p-6 lg:p-8">
        <div className="flex flex-col sm:flex-row sm:items-start gap-6">
          {/* Avatar */}
          {brand.logo_url ? (
            <img
              src={brand.logo_url}
              alt={brand.name}
              className="w-20 h-20 lg:w-24 lg:h-24 rounded-2xl object-cover flex-shrink-0"
            />
          ) : (
            <div className="w-20 h-20 lg:w-24 lg:h-24 rounded-2xl bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
              <span className="text-primary-600 dark:text-primary-400 font-bold text-3xl lg:text-4xl">
                {initial}
              </span>
            </div>
          )}

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <h1 className="text-2xl lg:text-3xl font-bold text-surface-900 dark:text-white">
                {brand.name}
              </h1>
              {price_tier && (
                <span className={`text-sm font-medium px-2.5 py-0.5 rounded-full ${colorClasses}`}>
                  {PRICE_TIER_LABELS[price_tier] || price_tier}
                </span>
              )}
              {brand.positioning?.brand_tone && (
                <span className="text-sm px-2.5 py-0.5 rounded-full bg-surface-100 text-surface-700 dark:bg-surface-800 dark:text-surface-300">
                  {brand.positioning.brand_tone}
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3 text-sm text-surface-500 dark:text-surface-400 mb-4">
              <span>{brand.country}</span>
              {brand.founded_year && brand.founded_year > 0 && (
                <>
                  <span className="text-surface-300 dark:text-surface-600">·</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    成立于 {brand.founded_year}
                  </span>
                </>
              )}
            </div>

            {brand.description && (
              <p className="text-surface-600 dark:text-surface-300 leading-relaxed mb-5 max-w-2xl">
                {brand.description}
              </p>
            )}

            {/* Action buttons - 官网 / 亚马逊 / IG / YouTube */}
            <div className="flex flex-wrap gap-2.5">
              {brand.website && (
                <a
                  href={brand.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium
                             bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300
                             rounded-lg hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
                >
                  <Globe className="w-4 h-4" />
                  官网
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {brand.amazon_url && (
                <a
                  href={brand.amazon_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium
                             bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400
                             rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
                >
                  <ShoppingCart className="w-4 h-4" />
                  亚马逊
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {brand.instagram_url && (
                <a
                  href={brand.instagram_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium
                             bg-pink-50 dark:bg-pink-900/20 text-pink-700 dark:text-pink-400
                             rounded-lg hover:bg-pink-100 dark:hover:bg-pink-900/30 transition-colors"
                >
                  <Instagram className="w-4 h-4" />
                  Instagram
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {brand.youtube_url && (
                <a
                  href={brand.youtube_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium
                             bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400
                             rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                >
                  <Youtube className="w-4 h-4" />
                  YouTube
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <button
                onClick={handleToggleCompare}
                className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors
                  ${
                    inBasket
                      ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-400 border border-primary-200 dark:border-primary-800'
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  }`}
              >
                {inBasket ? (
                  <>
                    <Check className="w-4 h-4" />
                    已加入对比
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    加入对比
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
