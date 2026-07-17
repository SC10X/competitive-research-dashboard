import { useState, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ChevronRight,
  ChevronDown,
  FolderTree,
  Dumbbell,
  Package,
  Layers,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import BrandCard from '@/components/brand/BrandCard'
import { getCategories } from '@/services/categoryApi'
import { getBrands } from '@/services/brandApi'
import type { CategoryTreeNode } from '@/types/brand'
import type { Brand } from '@/types/brand'

interface TreeNodeProps {
  node: CategoryTreeNode
  selectedSlug: string | null
  onSelect: (slug: string, name: string) => void
  expanded: Set<string>
  onToggle: (slug: string) => void
  depth?: number
}

function TreeNode({ node, selectedSlug, onSelect, expanded, onToggle, depth = 0 }: TreeNodeProps) {
  const hasChildren = Array.isArray(node.children) && node.children.length > 0
  const isExpanded = expanded.has(node.slug)
  const isSelected = selectedSlug === node.slug

  return (
    <div>
      <button
        type="button"
        onClick={() => {
          if (hasChildren) {
            onToggle(node.slug)
          }
          onSelect(node.slug, node.name)
        }}
        className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors ${
          isSelected
            ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
            : 'text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800'
        }`}
        style={{ paddingLeft: `${depth * 16 + 12}px` }}
      >
        {hasChildren ? (
          isExpanded ? (
            <ChevronDown className="h-4 w-4 flex-shrink-0 text-surface-400" />
          ) : (
            <ChevronRight className="h-4 w-4 flex-shrink-0 text-surface-400" />
          )
        ) : (
          <span className="w-4 flex-shrink-0" />
        )}
        <span className="flex-1 text-left truncate">{node.name}</span>
        {node.brand_count > 0 && (
          <span className="text-xs text-surface-400 bg-surface-100 dark:bg-surface-800 px-1.5 py-0.5 rounded">
            {node.brand_count}
          </span>
        )}
      </button>
      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              selectedSlug={selectedSlug}
              onSelect={onSelect}
              expanded={expanded}
              onToggle={onToggle}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const DIMENSIONS = [
  { key: 'product', label: '产品大类', icon: Layers, apiParam: 'product' },
  { key: 'scenario', label: '运动场景', icon: Dumbbell, apiParam: 'scenario' },
  { key: 'product-cat', label: '细化品类', icon: Package, apiParam: 'product-cat' },
] as const

export default function CategoriesPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const [selectedSlug, setSelectedSlug] = useState<string | null>(slug || null)
  const [selectedName, setSelectedName] = useState('')
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [dimension, setDimension] = useState<string>('product')

  // 按维度获取分类
  const { data: categoriesData, isLoading: catLoading } = useQuery({
    queryKey: ['categories', dimension],
    queryFn: async () => {
      const res = await getCategories(dimension === 'product' ? 'product' : dimension)
      return (res as any).data
    },
  })

  const { data: brandsData, isLoading: brandsLoading } = useQuery({
    queryKey: ['brands', 'category', selectedSlug],
    queryFn: async () => {
      const res = await getBrands({
        category: selectedSlug || undefined,
        page_size: 50,
      })
      return res.data
    },
    enabled: !!selectedSlug,
  })

  const categories = Array.isArray(categoriesData) ? categoriesData : []
  const brands = (brandsData?.items || []) as Brand[]

  const handleDimensionChange = useCallback((dim: string) => {
    setDimension(dim)
    setSelectedSlug(null)
    setSelectedName('')
    setExpanded(new Set())
  }, [])

  const breadcrumb = useMemo(() => {
    const parts: { name: string; slug: string }[] = [{ name: DIMENSIONS.find(d => d.key === dimension)?.label || '全部分类', slug: '' }]
    const findPath = (nodes: CategoryTreeNode[], target: string, path: {name: string, slug: string}[] = []): {name: string, slug: string}[] | null => {
      for (const node of nodes) {
        if (node.slug === target) return [...path, { name: node.name, slug: node.slug }]
        if (node.children && Array.isArray(node.children)) {
          const result = findPath(node.children, target, [...path, { name: node.name, slug: node.slug }])
          if (result) return result
        }
      }
      return null
    }
    if (selectedSlug) {
      const items = findPath(categories, selectedSlug)
      if (items) {
        items.forEach((item) => parts.push(item))
      }
    }
    return parts
  }, [categories, selectedSlug, dimension])

  const handleSelect = (catSlug: string, name: string) => {
    setSelectedSlug(catSlug)
    setSelectedName(name)
    navigate(`/categories/${catSlug}`, { replace: true })
  }

  const handleToggle = (nodeSlug: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(nodeSlug)) {
        next.delete(nodeSlug)
      } else {
        next.add(nodeSlug)
      }
      return next
    })
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">分类筛选</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          按多维度浏览品牌
        </p>
      </div>

      {/* Dimension Tabs */}
      <div className="flex gap-1 bg-surface-100 dark:bg-surface-800 rounded-lg p-1 w-fit">
        {DIMENSIONS.map((dim) => {
          const Icon = dim.icon
          const isActive = dimension === dim.key
          return (
            <button
              key={dim.key}
              type="button"
              onClick={() => handleDimensionChange(dim.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-white dark:bg-surface-700 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200'
              }`}
            >
              <Icon className="h-4 w-4" />
              {dim.label}
            </button>
          )
        })}
      </div>

      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-sm text-surface-500 dark:text-surface-400">
        {breadcrumb.map((part, index) => (
          <span key={index} className="flex items-center gap-1.5">
            {index > 0 && <ChevronRight className="h-3.5 w-3.5" />}
            {index < breadcrumb.length - 1 ? (
              <button
                type="button"
                onClick={() => handleSelect(part.slug, part.name)}
                className="hover:text-primary-600 dark:hover:text-primary-400"
              >
                {part.name}
              </button>
            ) : (
              <span className="text-surface-900 dark:text-white font-medium">{part.name}</span>
            )}
          </span>
        ))}
      </div>

      <div className="flex gap-6">
        {/* Category Tree */}
        <div className="w-64 flex-shrink-0">
          <Card padding="sm">
            <div className="flex items-center gap-2 px-2 py-2 mb-1">
              <FolderTree className="h-4 w-4 text-surface-400" />
              <span className="text-sm font-semibold text-surface-900 dark:text-white">
                {DIMENSIONS.find(d => d.key === dimension)?.label || '分类'}目录
              </span>
            </div>
            {catLoading ? (
              <Skeleton variant="text" />
            ) : categories.length === 0 ? (
              <EmptyState title="暂无分类" />
            ) : (
              <div className="space-y-0.5">
                {categories.map((node) => (
                  <TreeNode
                    key={node.id}
                    node={node}
                    selectedSlug={selectedSlug}
                    onSelect={handleSelect}
                    expanded={expanded}
                    onToggle={handleToggle}
                  />
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Brands Grid */}
        <div className="flex-1 min-w-0">
          {brandsLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} variant="card" />
              ))}
            </div>
          ) : brands.length === 0 ? (
            <EmptyState
              title="暂无品牌"
              description={selectedSlug ? '该分类下暂无品牌' : '请从左侧选择分类'}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {brands.map((brand) => (
                <BrandCard key={brand.id} brand={brand} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
