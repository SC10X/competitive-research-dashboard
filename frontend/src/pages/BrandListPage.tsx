import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LayoutGrid, List } from 'lucide-react'
import { SearchInput } from '@/components/ui/SearchInput'
import { FilterDropdown } from '@/components/ui/FilterDropdown'
import { Toggle } from '@/components/ui/Toggle'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import BrandCard from '@/components/brand/BrandCard'
import BrandTable from '@/components/brand/BrandTable'
import { getBrands } from '@/services/brandApi'
import { getCategories } from '@/services/categoryApi'

import type { Brand } from '@/types/brand'

interface PaginationControlsProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

function PaginationControls({ currentPage, totalPages, onPageChange }: PaginationControlsProps) {
  const pages = useMemo(() => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    const pages: (number | 'ellipsis')[] = [1]

    if (currentPage > 3) {
      pages.push('ellipsis')
    }

    const start = Math.max(2, currentPage - 1)
    const end = Math.min(totalPages - 1, currentPage + 1)

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }

    if (currentPage < totalPages - 2) {
      pages.push('ellipsis')
    }

    pages.push(totalPages)

    return pages
  }, [currentPage, totalPages])

  return (
    <div className="flex items-center justify-center gap-2">
      <button
        type="button"
        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage <= 1}
        className="px-3 py-2 text-sm font-medium rounded-lg border border-surface-200 dark:border-surface-700 text-surface-600 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-800 disabled:opacity-30 disabled:cursor-not-allowed"
      >
        上一页
      </button>
      {pages.map((page, index) =>
        page === 'ellipsis' ? (
          <span key={`ellipsis-${index}`} className="text-surface-400 px-2">
            ...
          </span>
        ) : (
          <button
            key={page}
            type="button"
            onClick={() => onPageChange(page)}
            className={`w-10 h-10 text-sm font-medium rounded-lg transition-colors ${
              page === currentPage
                ? 'bg-primary-600 text-white dark:bg-primary-500'
                : 'text-surface-600 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-800 border border-surface-200 dark:border-surface-700'
            }`}
          >
            {page}
          </button>
        )
      )}
      <button
        type="button"
        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage >= totalPages}
        className="px-3 py-2 text-sm font-medium rounded-lg border border-surface-200 dark:border-surface-700 text-surface-600 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-800 disabled:opacity-30 disabled:cursor-not-allowed"
      >
        下一页
      </button>
    </div>
  )
}

export default function BrandListPage() {
  const [search, setSearch] = useState('')
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [selectedPriceTiers, setSelectedPriceTiers] = useState<string[]>([])
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const [viewMode, setViewMode] = useState('card')
  const [page, setPage] = useState(1)
  const pageSize = 12

  const { data: brandsData, isLoading } = useQuery({
    queryKey: ['brands', search, selectedCategories, selectedPriceTiers, selectedCountries, page],
    queryFn: async () => {
      const res = await getBrands({
        search: search || undefined,
        category: selectedCategories.length > 0 ? selectedCategories[0] : undefined,
        price_tier: selectedPriceTiers.length > 0 ? selectedPriceTiers.join(',') : undefined,
        country: selectedCountries.length > 0 ? selectedCountries.join(',') : undefined,
        page,
        page_size: pageSize,
      })
      return res.data
    },
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const res = await getCategories()
      return res.data
    },
  })

  const brands = (brandsData?.items || []) as Brand[]
  const totalBrands = brandsData?.total || 0

  const totalPages = Math.max(1, Math.ceil(totalBrands / pageSize))

  const categoryOptions = useMemo(() => {
    const cats = Array.isArray(categoriesData) ? categoriesData : []
    const opts: { value: string; label: string }[] = []
    const walk = (nodes: typeof cats) => {
      for (const node of nodes) {
        opts.push({ value: node.slug, label: node.name })
        if (node.children) walk(node.children)
      }
    }
    walk(cats)
    return opts
  }, [categoriesData])

  const priceTierOptions = [
    { value: 'Luxury', label: '奢侈' },
    { value: 'Premium', label: '高端' },
    { value: 'Mid', label: '中端' },
    { value: 'Mass', label: '平价' },
  ]

  const countryOptions = useMemo(() => {
    const countries = new Set<string>()
    brands.forEach((b) => {
      if (b.country) countries.add(b.country)
    })
    return Array.from(countries).map((c) => ({ value: c, label: c }))
  }, [brands])

  const viewOptions = [
    { value: 'card', label: '卡片', icon: <LayoutGrid className="h-4 w-4" /> },
    { value: 'table', label: '表格', icon: <List className="h-4 w-4" /> },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">品牌列表</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          浏览和筛选北美服饰鞋包品牌
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={search}
          onChange={(v) => {
            setSearch(v)
            setPage(1)
          }}
          placeholder="搜索品牌名称..."
          className="w-full sm:w-64"
        />
        <FilterDropdown
          label="分类"
          options={categoryOptions}
          selected={selectedCategories}
          onChange={(v) => {
            setSelectedCategories(v)
            setPage(1)
          }}
          searchable
        />
        <FilterDropdown
          label="价格带"
          options={priceTierOptions}
          selected={selectedPriceTiers}
          onChange={(v) => {
            setSelectedPriceTiers(v)
            setPage(1)
          }}
        />
        <FilterDropdown
          label="国家"
          options={countryOptions}
          selected={selectedCountries}
          onChange={(v) => {
            setSelectedCountries(v)
            setPage(1)
          }}
          searchable
        />
        <div className="ml-auto">
          <Toggle options={viewOptions} value={viewMode} onChange={setViewMode} />
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      ) : brands.length === 0 ? (
        <EmptyState
          title="未找到品牌"
          description="请尝试调整筛选条件或搜索关键词"
        />
      ) : viewMode === 'card' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {brands.map((brand) => (
            <BrandCard key={brand.id} brand={brand} />
          ))}
        </div>
      ) : (
        <BrandTable brands={brands} />
      )}

      {/* Pagination */}
      {totalPages > 1 && !isLoading && (
        <PaginationControls
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </div>
  )
}
