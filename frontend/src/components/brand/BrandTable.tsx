import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Brand } from '@/types/brand'
import { PRICE_TIER_LABELS, PRICE_TIER_COLORS } from '@/types/brand'
import { formatNumber } from '@/utils/format'
import { useCompareStore } from '@/store/compareStore'
import { Plus, Check, ArrowUpDown, ArrowUp, ArrowDown, ExternalLink, Users, Globe } from 'lucide-react'

interface BrandTableProps {
  brands: Brand[]
}

type SortField = 'name' | 'country' | 'price_tier' | 'founded_year' | 'monthly_web_visits'
type SortDirection = 'asc' | 'desc'

export default function BrandTable({ brands }: BrandTableProps) {
  const navigate = useNavigate()
  const { addItem, removeItem, isInBasket } = useCompareStore()
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const getSocialFollowers = (brand: Brand) => {
    return brand.instagram_followers || 0
  }

  const sortedBrands = useMemo(() => {
    const sorted = [...brands]
    sorted.sort((a, b) => {
      let valA: string | number
      let valB: string | number

      switch (sortField) {
        case 'name':
          valA = a.name.toLowerCase()
          valB = b.name.toLowerCase()
          break
        case 'country':
          valA = a.country.toLowerCase()
          valB = b.country.toLowerCase()
          break
        case 'price_tier':
          valA = a.price_tier || ''
          valB = b.price_tier || ''
          break
        case 'founded_year':
          valA = a.founded_year || 0
          valB = b.founded_year || 0
          break
        case 'monthly_web_visits':
          valA = a.monthly_web_visits || 0
          valB = b.monthly_web_visits || 0
          break
        default:
          valA = a.name.toLowerCase()
          valB = b.name.toLowerCase()
      }

      if (valA < valB) return sortDirection === 'asc' ? -1 : 1
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1
      return 0
    })
    return sorted
  }, [brands, sortField, sortDirection])

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="w-3.5 h-3.5 opacity-40" />
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400" />
    )
  }

  const ThButton = ({
    field,
    children,
    className = '',
  }: {
    field: SortField
    children: React.ReactNode
    className?: string
  }) => (
    <th
      className={`px-4 py-3 text-left text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider cursor-pointer select-none hover:text-surface-700 dark:hover:text-surface-300 ${className}`}
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1.5">
        {children}
        <SortIcon field={field} />
      </div>
    </th>
  )

  if (brands.length === 0) {
    return (
      <div className="text-center py-12 text-surface-400 dark:text-surface-500">
        <p className="text-lg">暂无品牌数据</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-surface-200 dark:border-surface-700">
      <table className="w-full">
        <thead>
          <tr className="bg-surface-50 dark:bg-surface-800/50 border-b border-surface-200 dark:border-surface-700">
            <ThButton field="name">品牌名称</ThButton>
            <ThButton field="country">国家</ThButton>
            <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
              价格带
            </th>
            <ThButton field="founded_year">成立年份</ThButton>
            <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
              分类
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
              <div className="flex items-center justify-end gap-1">
                <Users className="w-3.5 h-3.5" />
                社媒粉丝
              </div>
            </th>
            <ThButton field="monthly_web_visits">
              <div className="flex items-center gap-1">
                <Globe className="w-3.5 h-3.5" />
                官网流量
              </div>
            </ThButton>
            <th className="px-4 py-3 text-right text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-100 dark:divide-surface-800">
          {sortedBrands.map((brand) => {
            const inBasket = isInBasket(brand.id)
            const initial = brand.name.charAt(0).toUpperCase()
            const socialFollowers = getSocialFollowers(brand)
            const colorClasses =
              PRICE_TIER_COLORS[brand.price_tier || ''] ||
              'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'

            return (
              <tr
                key={brand.id}
                className="bg-white dark:bg-surface-900 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {brand.logo_url ? (
                      <img
                        src={brand.logo_url}
                        alt={brand.name}
                        className="w-8 h-8 rounded-lg object-cover flex-shrink-0"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
                        <span className="text-primary-600 dark:text-primary-400 font-bold text-xs">
                          {initial}
                        </span>
                      </div>
                    )}
                    <button
                      onClick={() => navigate(`/brands/${brand.slug}`)}
                      className="text-sm font-medium text-surface-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 text-left transition-colors"
                    >
                      {brand.name}
                    </button>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-surface-600 dark:text-surface-400">
                  {brand.country}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colorClasses}`}>
                    {PRICE_TIER_LABELS[brand.price_tier || ''] || brand.price_tier || '-'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-surface-600 dark:text-surface-400">
                  {brand.founded_year || '-'}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {brand.categories && brand.categories.slice(0, 2).map((cat) => (
                      <span
                        key={cat.id}
                        className="text-xs px-1.5 py-0.5 rounded bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400"
                      >
                        {cat.name}
                      </span>
                    ))}
                    {brand.categories && brand.categories.length > 2 && (
                      <span className="text-xs text-surface-400">+{brand.categories.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-right text-surface-600 dark:text-surface-400">
                  {socialFollowers > 0 ? formatNumber(socialFollowers) : '-'}
                </td>
                <td className="px-4 py-3 text-sm text-right text-surface-600 dark:text-surface-400">
                  {brand.monthly_web_visits && brand.monthly_web_visits > 0
                    ? formatNumber(brand.monthly_web_visits)
                    : '-'}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => navigate(`/brands/${brand.slug}`)}
                      className="p-1.5 rounded-lg text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
                      title="查看详情"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() =>
                        inBasket
                          ? removeItem(brand.id)
                          : addItem({ id: brand.id, name: brand.name, slug: brand.slug, price_tier: brand.price_tier, logo_url: brand.logo_url })
                      }
                      className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors
                        ${
                          inBasket
                            ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-400'
                            : 'text-surface-500 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800'
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
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
