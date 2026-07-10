import { useState, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  X,
  Plus,
  Search,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { getBrands } from '@/services/brandApi'
import { queryCompare } from '@/services/compareApi'
import { useCompareStore } from '@/store/compareStore'
import { formatNumber, formatCurrency } from '@/utils/format'
import { DIMENSIONS } from '@/utils/constants'
import type { Brand } from '@/types/brand'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts'

const RADAR_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
const BAR_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export default function ComparePage() {
  const { items: basketBrands, removeItem, addItem, clearAll } = useCompareStore()
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(
    DIMENSIONS.slice(0, 6).map((d) => d.key)
  )
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)

  const { data: allBrandsData } = useQuery({
    queryKey: ['brands', 'all'],
    queryFn: async () => {
      const res = await getBrands({ page_size: 100 })
      return res.data
    },
  })

  const allBrands = (allBrandsData?.items || []) as Brand[]

  const { data: compareData, isLoading: compareLoading } = useQuery({
    queryKey: ['compare', basketBrands.map((b) => b.slug), selectedDimensions],
    queryFn: async () => {
      if (basketBrands.length < 2) return null
      const res = await queryCompare(
        basketBrands.map((b) => b.slug),
        selectedDimensions
      )
      return res.data
    },
    enabled: basketBrands.length >= 2,
  })

  const selectedIds = useMemo(() => new Set(basketBrands.map((b) => b.id)), [basketBrands])

  const filteredBrands = useMemo(() => {
    if (!searchQuery) return allBrands.filter((b) => !selectedIds.has(b.id))
    const q = searchQuery.toLowerCase()
    return allBrands.filter(
      (b) =>
        !selectedIds.has(b.id) &&
        (b.name.toLowerCase().includes(q) || b.country.toLowerCase().includes(q))
    )
  }, [allBrands, selectedIds, searchQuery])

  const radarData = useMemo(() => {
    if (!compareData || !Array.isArray(compareData.data)) return []
    // Build normalized scores from actual dimension data
    // For each dimension, find min/max across brands and normalize to 0-100
    const dimScores: Record<string, Record<string, number>> = {}
    const dimRaw: Record<string, Record<string, number>> = {}
    
    compareData.data.forEach((item) => {
      if (!dimRaw[item.dimension]) dimRaw[item.dimension] = {}
      const dimData = item.data as Record<string, unknown>
      let rawScore = 0
      if (dimData) {
        if (dimData.price_tier) {
          const tierMap: Record<string, number> = { Luxury: 5, Premium: 4, 'Mid-Premium': 3, Mid: 2, Mass: 1 }
          rawScore = tierMap[dimData.price_tier as string] || 2
        } else if (dimData.engagement_rate !== undefined) {
          rawScore = dimData.engagement_rate as number
        } else if (dimData.revenue !== undefined) {
          rawScore = dimData.revenue as number
        } else if (dimData.rating !== undefined) {
          rawScore = dimData.rating as number
        } else if (dimData.dtc_pct !== undefined) {
          rawScore = dimData.dtc_pct as number
        } else if (dimData.followers !== undefined) {
          rawScore = Math.log10((dimData.followers as number) + 1)
        }
      }
      dimRaw[item.dimension][item.brand_name] = rawScore
    })
    
    // Normalize each dimension to 0-100
    Object.keys(dimRaw).forEach((dim) => {
      dimScores[dim] = {}
      const values = Object.values(dimRaw[dim])
      const minVal = Math.min(...values, 0)
      const maxVal = Math.max(...values, 1)
      const range = maxVal - minVal || 1
      Object.keys(dimRaw[dim]).forEach((brand) => {
        dimScores[dim][brand] = Math.round(((dimRaw[dim][brand] - minVal) / range) * 100)
      })
    })
    
    return selectedDimensions.map((dim) => {
      const dimLabel = DIMENSIONS.find((d) => d.key === dim)?.label || dim
      const entry: Record<string, unknown> = { dimension: dimLabel }
      basketBrands.forEach((b) => {
        entry[b.name] = dimScores[dim]?.[b.name] ?? 0
      })
      return entry
    })
  }, [compareData, selectedDimensions, basketBrands])

  const barData = useMemo(() => {
    if (!compareData || !Array.isArray(compareData.data)) return []
    return basketBrands.map((b) => {
      const socialItem = compareData.data.find(
        (d) => d.brand_slug === b.slug && d.dimension === 'social_media'
      )
      const socialList = socialItem?.data as Array<Record<string, unknown>> | undefined
      const instagram = socialList?.find((s: Record<string, unknown>) => s.platform === 'Instagram')
      return {
        name: b.name,
        followers: instagram?.followers as number || 0,
      }
    })
  }, [compareData, basketBrands])

  const scatterData = useMemo(() => {
    if (!compareData || !Array.isArray(compareData.data)) return []
    return basketBrands.map((b) => {
      const posItem = compareData.data.find(
        (d) => d.brand_slug === b.slug && d.dimension === 'positioning'
      )
      const socItem = compareData.data.find(
        (d) => d.brand_slug === b.slug && d.dimension === 'social_media'
      )
      const finItem = compareData.data.find(
        (d) => d.brand_slug === b.slug && d.dimension === 'financials'
      )

      const posData = posItem?.data as Record<string, unknown> | undefined
      const socData = socItem?.data as Array<Record<string, unknown>> | undefined
      const finData = finItem?.data as Array<Record<string, unknown>> | undefined

      // Price positioning: Luxury=90, Premium=70, etc.
      const tierScores: Record<string, number> = { Luxury: 90, Premium: 70, 'Mass Premium': 55, Mid: 40, Mass: 25 }
      const x = posData?.price_tier ? (tierScores[posData.price_tier as string] || 50) : 50

      // Social influence from Instagram followers
      const instagram = socData?.find((s: Record<string, unknown>) => s.platform === 'Instagram')
      const y = instagram?.followers ? Math.min(100, Math.log10(instagram.followers as number) * 12) : 30

      // Revenue bubble size
      const latestFin = finData?.sort((a, b) => ((b.fiscal_year as number) || 0) - ((a.fiscal_year as number) || 0))[0]
      const z = latestFin?.revenue ? Math.min(100, Math.log10((latestFin.revenue as number) + 1) * 8) : 50

      return { name: b.name, x, y, z }
    })
  }, [compareData, basketBrands])

  const comparisonTable = useMemo(() => {
    if (!compareData || !Array.isArray(compareData.data)) return []
    return basketBrands.map((b) => {
      const brand = allBrands.find((ab) => ab.id === b.id)

      const posItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'positioning')
      const posData = posItem?.data as Record<string, unknown> | undefined

      const demItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'demographics')
      const demData = demItem?.data as Record<string, unknown> | undefined

      const chItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'channel_strategy')
      const chData = chItem?.data as Record<string, unknown> | undefined

      const socItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'social_media')
      const socData = socItem?.data as Array<Record<string, unknown>> | undefined
      const instagram = socData?.find((s) => s.platform === 'Instagram')

      const digItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'digital')
      const digData = digItem?.data as Record<string, unknown> | undefined

      const finItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'financials')
      const finData = finItem?.data as Array<Record<string, unknown>> | undefined
      const latestFin = finData?.sort((a, b) => ((b.fiscal_year as number) || 0) - ((a.fiscal_year as number) || 0))[0]

      const senItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'sentiment')
      const senData = senItem?.data as Array<Record<string, unknown>> | undefined

      const prItem = compareData.data.find((d) => d.brand_slug === b.slug && d.dimension === 'pricing')
      const prData = prItem?.data as Array<Record<string, unknown>> | undefined

      return {
        name: b.name,
        priceTier: posData?.price_tier as string || '-',
        avgPrice: prData && prData.length > 0 ? `$${prData[0].avg_price || '-'}` : '-',
        demographics: demData
          ? `${demData.age_range || '-'} / ${demData.gender_skew || '-'}`
          : '-',
        dtcPct: chData?.dtc_pct != null ? `${chData.dtc_pct}%` : '-',
        socialFollowers: instagram?.followers ? formatNumber(instagram.followers as number) : '-',
        monthlyTraffic: digData?.monthly_web_visits ? formatNumber(digData.monthly_web_visits as number) : '-',
        revenue: latestFin?.revenue ? formatCurrency(latestFin.revenue as number) : '-',
        rating: senData && senData.length > 0 ? String(senData[0].rating || '-') : '-',
      }
    })
  }, [compareData, allBrands, basketBrands])

  const handleAddBrand = useCallback(
    (brand: Brand) => {
      addItem(brand)
      setSearchQuery('')
      setShowSearch(false)
    },
    [addItem]
  )

  const toggleDimension = useCallback((key: string) => {
    setSelectedDimensions((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    )
  }, [])

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">多维对比</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          选择品牌和维度进行多维度竞品对比分析
        </p>
      </div>

      {/* Brand Selection */}
      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-surface-500 dark:text-surface-400 mr-2">
            已选品牌 ({basketBrands.length}/6)：
          </span>
          {basketBrands.map((brand) => (
            <Badge key={brand.id} variant="primary" size="md" className="flex items-center gap-1">
              {brand.name}
              <button
                onClick={() => removeItem(brand.id)}
                className="ml-1 hover:text-red-500"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
          {basketBrands.length < 6 && (
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSearch(!showSearch)}
              >
                <Plus className="h-4 w-4" />
                添加品牌
              </Button>
              {showSearch && (
                <div className="absolute top-full mt-1 left-0 w-72 bg-white dark:bg-surface-900 rounded-lg border border-surface-200 dark:border-surface-700 shadow-lg z-20">
                  <div className="p-2 border-b border-surface-100 dark:border-surface-800">
                    <div className="relative">
                      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-surface-400" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="搜索品牌..."
                        className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 text-surface-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                      />
                    </div>
                  </div>
                  <div className="max-h-48 overflow-y-auto">
                    {filteredBrands.slice(0, 10).map((brand) => (
                      <button
                        key={brand.id}
                        type="button"
                        onClick={() => handleAddBrand(brand)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 text-left hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                      >
                        <span className="text-sm font-medium text-surface-900 dark:text-white">
                          {brand.name}
                        </span>
                        <span className="text-xs text-surface-400">{brand.country}</span>
                      </button>
                    ))}
                    {filteredBrands.length === 0 && (
                      <p className="px-3 py-4 text-sm text-surface-400 text-center">
                        未找到更多品牌
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
          {basketBrands.length > 0 && (
            <Button variant="ghost" size="sm" onClick={clearAll} className="text-red-500">
              清空
            </Button>
          )}
        </div>
      </Card>

      {/* Dimension Selection */}
      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-surface-500 dark:text-surface-400 mr-2">
            选择维度：
          </span>
          {DIMENSIONS.map((dim) => (
            <button
              key={dim.key}
              type="button"
              onClick={() => toggleDimension(dim.key)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                selectedDimensions.includes(dim.key)
                  ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                  : 'border-surface-200 text-surface-500 hover:bg-surface-50 dark:border-surface-700 dark:text-surface-400 dark:hover:bg-surface-800'
              }`}
            >
              {dim.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Comparison Table */}
      {basketBrands.length >= 2 ? (
        <div className="space-y-6">
          <Card>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
              对比表格
            </h2>
            {compareLoading ? (
              <Skeleton variant="table-row" />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-surface-200 dark:border-surface-700">
                      <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        品牌
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        价格带
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        均价
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        目标人群
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        DTC占比
                      </th>
                      <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        社媒粉丝
                      </th>
                      <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        月访问量
                      </th>
                      <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        营收
                      </th>
                      <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                        评分
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonTable.map((row) => (
                      <tr
                        key={row.name}
                        className="border-b border-surface-100 dark:border-surface-800 hover:bg-surface-50 dark:hover:bg-surface-800/50"
                      >
                        <td className="py-3 px-4 font-medium text-surface-900 dark:text-white">
                          {row.name}
                        </td>
                        <td className="py-3 px-4 text-surface-600 dark:text-surface-400">
                          {row.priceTier}
                        </td>
                        <td className="py-3 px-4 text-surface-600 dark:text-surface-400">
                          {row.avgPrice}
                        </td>
                        <td className="py-3 px-4 text-surface-600 dark:text-surface-400">
                          {row.demographics}
                        </td>
                        <td className="py-3 px-4 text-surface-600 dark:text-surface-400">
                          {row.dtcPct}
                        </td>
                        <td className="py-3 px-4 text-right text-surface-600 dark:text-surface-400">
                          {row.socialFollowers}
                        </td>
                        <td className="py-3 px-4 text-right text-surface-600 dark:text-surface-400">
                          {row.monthlyTraffic}
                        </td>
                        <td className="py-3 px-4 text-right text-surface-600 dark:text-surface-400">
                          {row.revenue}
                        </td>
                        <td className="py-3 px-4 text-right text-surface-600 dark:text-surface-400">
                          {row.rating}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Radar Chart */}
          <Card>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
              多维度雷达图
            </h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis
                    dataKey="dimension"
                    tick={{ fontSize: 12 }}
                  />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  {basketBrands.map((brand, index) => (
                    <Radar
                      key={brand.id}
                      name={brand.name}
                      dataKey={brand.name}
                      stroke={RADAR_COLORS[index % RADAR_COLORS.length]}
                      fill={RADAR_COLORS[index % RADAR_COLORS.length]}
                      fillOpacity={0.1}
                    />
                  ))}
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Bar Chart */}
          <Card>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
              Instagram 粉丝数对比
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatNumber(v)} />
                  <Tooltip formatter={(value: number) => [formatNumber(value), '粉丝数']} />
                  <Bar dataKey="followers" radius={[4, 4, 0, 0]}>
                    {barData.map((_, index) => (
                      <rect key={`rect-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Scatter Chart */}
          <Card>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
              双变量散点分析
            </h2>
            <p className="text-sm text-surface-500 dark:text-surface-400 mb-4">
              X轴：价格定位 | Y轴：社媒影响力 | 气泡大小：营收规模
            </p>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="价格定位"
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="社媒影响力"
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                  />
                  <ZAxis type="number" dataKey="z" range={[60, 400]} />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    formatter={(value: number, name: string) => [value.toFixed(0), name]}
                  />
                  <Legend />
                  {scatterData.map((_, index) => (
                    <Scatter
                      key={`scatter-${index}`}
                      name={scatterData[index]?.name || `品牌${index + 1}`}
                      data={[scatterData[index]]}
                      fill={RADAR_COLORS[index % RADAR_COLORS.length]}
                    />
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      ) : (
        <EmptyState
          title="请选择品牌"
          description="至少选择 2 个品牌进行对比分析。点击「添加品牌」按钮或从品牌列表中将品牌加入对比篮。"
        />
      )}
    </div>
  )
}
