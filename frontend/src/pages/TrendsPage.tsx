import { useState, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { getBrands } from '@/services/brandApi'
import { getRevenueTrend } from '@/services/trendApi'
import { useTrendStore } from '@/store/trendStore'
import { formatNumber, formatCurrency } from '@/utils/format'
import type { Brand } from '@/types/brand'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const LINE_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export default function TrendsPage() {
  const { items: basketBrands, addItem, removeItem } = useTrendStore()
  const [selectedMetric, setSelectedMetric] = useState<'revenue' | 'social'>('revenue')
  const currentYear = new Date().getFullYear()
  const [yearStart, setYearStart] = useState(currentYear - 5)
  const [yearEnd, setYearEnd] = useState(currentYear - 1)

  const { data: allBrandsData } = useQuery({
    queryKey: ['brands', 'all'],
    queryFn: async () => {
      const res = await getBrands({ page_size: 100 })
      return res.data
    },
  })

  const allBrands = (allBrandsData?.items || []) as Brand[]

  const selectedBrandSlugs = useMemo(() => basketBrands.map((b) => b.slug), [basketBrands])

  const { data: trendData, isLoading } = useQuery({
    queryKey: ['trends', 'revenue', selectedBrandSlugs, yearStart, yearEnd],
    queryFn: async () => {
      if (selectedBrandSlugs.length === 0) return []
      const res = await getRevenueTrend(selectedBrandSlugs)
      return Array.isArray(res.data) ? res.data : []
    },
    enabled: selectedBrandSlugs.length > 0,
  })

  const chartData = useMemo(() => {
    if (!trendData) return []
    const years = Array.from(
      { length: yearEnd - yearStart + 1 },
      (_, i) => yearStart + i
    )
    return years.map((year) => {
      const point: Record<string, string | number> = { year }
      basketBrands.forEach((brand) => {
        const brandPoint = trendData?.find(
          (d) => d.fiscal_year === year && d.brand_name === brand.name
        )
        point[brand.name] = brandPoint?.revenue || 0
      })
      return point
    })
  }, [trendData, basketBrands, yearStart, yearEnd])

  const tableData = useMemo(() => {
    if (!trendData) return []
    const brandMap = new Map<string, { total: number; growth: number }>()
    basketBrands.forEach((brand) => {
      const brandPoints = trendData.filter((d) => d.brand_name === brand.name)
      const total = brandPoints.reduce((sum, p) => sum + (p.revenue || 0), 0)
      const sorted = brandPoints.sort((a, b) => a.fiscal_year - b.fiscal_year)
      const first = sorted[0]
      const last = sorted[sorted.length - 1]
      const firstRev = first?.revenue || 0
      const growth = firstRev > 0 ? (((last?.revenue || 0) - firstRev) / firstRev) * 100 : 0
      brandMap.set(brand.name, { total, growth })
    })
    return basketBrands.map((brand) => ({
      name: brand.name,
      total: brandMap.get(brand.name)?.total || 0,
      growth: brandMap.get(brand.name)?.growth || 0,
    }))
  }, [trendData, basketBrands])

  const toggleBrand = useCallback(
    (brand: Brand) => {
      if (basketBrands.some((b) => b.id === brand.id)) {
        removeItem(brand.id)
      } else {
        if (basketBrands.length < 6) {
          addItem(brand)
        }
      }
    },
    [basketBrands, addItem, removeItem]
  )

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">趋势分析</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          多品牌营收与社媒趋势对比
        </p>
      </div>

      {/* Controls */}
      <Card>
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-surface-500 dark:text-surface-400 mb-2">
              选择品牌（最多6个）：
            </p>
            <div className="flex flex-wrap gap-2">
              {basketBrands.map((brand) => (
                <Badge key={brand.id} variant="primary" size="md" className="flex items-center gap-1">
                  {brand.name}
                  <button
                    onClick={() => removeItem(brand.id)}
                    className="ml-1 hover:text-red-500"
                  >
                    &times;
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {allBrands.slice(0, 12).map((brand) => {
                const isSelected = basketBrands.some((b) => b.id === brand.id)
                return (
                  <button
                    key={brand.id}
                    type="button"
                    onClick={() => toggleBrand(brand)}
                    className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                      isSelected
                        ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                        : 'border-surface-200 text-surface-500 hover:bg-surface-50 dark:border-surface-700 dark:text-surface-400 dark:hover:bg-surface-800'
                    }`}
                  >
                    {brand.name}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="text-sm font-medium text-surface-500 dark:text-surface-400 mr-2">
                指标：
              </label>
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value as 'revenue' | 'social')}
                className="rounded-lg border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 px-3 py-1.5 text-sm text-surface-900 dark:text-white"
              >
                <option value="revenue">营收</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-surface-500 dark:text-surface-400 mr-2">
                年份：
              </label>
              <select
                value={yearStart}
                onChange={(e) => setYearStart(Number(e.target.value))}
                className="rounded-lg border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 px-3 py-1.5 text-sm text-surface-900 dark:text-white mr-2"
              >
                {Array.from({ length: currentYear - 2017 }, (_, i) => 2018 + i).map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
              <span className="text-surface-400 mx-1">-</span>
              <select
                value={yearEnd}
                onChange={(e) => setYearEnd(Number(e.target.value))}
                className="rounded-lg border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 px-3 py-1.5 text-sm text-surface-900 dark:text-white"
              >
                {Array.from({ length: currentYear - 2019 }, (_, i) => 2020 + i).map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Chart */}
      {basketBrands.length === 0 ? (
        <EmptyState
          title="请选择品牌"
          description="至少选择 1 个品牌以查看趋势数据"
        />
      ) : isLoading ? (
        <Skeleton variant="chart" />
      ) : (
        <Card>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
            {selectedMetric === 'revenue' ? '营收趋势' : '社媒粉丝趋势'}
          </h2>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickFormatter={(v) =>
                    selectedMetric === 'revenue' ? formatCurrency(v) : formatNumber(v)
                  }
                />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    selectedMetric === 'revenue' ? formatCurrency(value) : formatNumber(value),
                    name,
                  ]}
                />
                <Legend />
                {basketBrands.map((brand, index) => (
                  <Line
                    key={brand.id}
                    type="monotone"
                    dataKey={brand.name}
                    stroke={LINE_COLORS[index % LINE_COLORS.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Data Table */}
      {tableData.length > 0 && (
        <Card>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
            趋势数据表
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200 dark:border-surface-700">
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                    品牌
                  </th>
                  <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                    累计营收
                  </th>
                  <th className="text-right py-3 px-4 font-medium text-surface-500 dark:text-surface-400">
                    期间增长率
                  </th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row) => (
                  <tr
                    key={row.name}
                    className="border-b border-surface-100 dark:border-surface-800 hover:bg-surface-50 dark:hover:bg-surface-800/50"
                  >
                    <td className="py-3 px-4 font-medium text-surface-900 dark:text-white">
                      {row.name}
                    </td>
                    <td className="text-right py-3 px-4 text-surface-600 dark:text-surface-400">
                      {formatCurrency(row.total)}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1 ${
                          row.growth >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        <TrendingUp className="h-3.5 w-3.5" />
                        {row.growth.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
