import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Building2,
  GitCompare,
  Activity,
  Clock,
  TrendingUp,
  ShoppingBag,
  Footprints,
  Briefcase,
  ArrowRight,
} from 'lucide-react'
import { StatCard } from '@/components/ui/StatCard'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import BrandCardMini from '@/components/brand/BrandCardMini'
import { getStatsOverview, getCategoryDistribution } from '@/services/statsApi'
import { getEvents } from '@/services/eventApi'
import { getBrands } from '@/services/brandApi'
import type { StatsOverview, CategoryDistribution } from '@/services/statsApi'
import type { CompetitiveEvent, Brand } from '@/types/brand'
import { EVENT_TYPE_LABELS } from '@/types/brand'

export default function HomePage() {
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['stats', 'overview'],
    queryFn: async () => {
      const res = await getStatsOverview()
      return res.data
    },
  })

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['events', 'recent'],
    queryFn: async () => {
      const res = await getEvents({ page: 1, page_size: 5 })
      return res.data
    },
  })

  const { data: brandsData, isLoading: brandsLoading } = useQuery({
    queryKey: ['brands', 'featured'],
    queryFn: async () => {
      const res = await getBrands({ page: 1, page_size: 8 })
      return res.data
    },
  })

  const stats = statsData as StatsOverview | undefined
  const events = (eventsData?.items || []) as CompetitiveEvent[]
  const brands = (brandsData?.items || []) as Brand[]

  const { data: catDistData } = useQuery({
    queryKey: ['stats', 'category-distribution'],
    queryFn: async () => {
      const res = await getCategoryDistribution()
      return res.data
    },
  })
  const catDist = (catDistData || []) as CategoryDistribution[]
  const catCounts = {
    apparel: catDist.find(c => c.slug === 'apparel')?.count ?? 0,
    footwear: catDist.find(c => c.slug === 'footwear')?.count ?? 0,
    bags: catDist.find(c => c.slug === 'bags')?.count ?? 0,
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">首页仪表盘</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">北美服饰鞋包竞对品牌研究看板</p>
      </div>

      {/* Stats Row */}
      {statsLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="品牌总数"
            value={stats.total_brands}
            icon={<Building2 className="h-5 w-5" />}
          />
          <StatCard
            title="活跃对比组"
            value={stats.active_brands}
            icon={<GitCompare className="h-5 w-5" />}
          />
          <StatCard
            title="竞对动态（本月）"
            value={stats.events_this_month ?? stats.total_events}
            icon={<Activity className="h-5 w-5" />}
          />
          <StatCard
            title="数据更新时间"
            value={stats.last_updated_at
              ? new Date(stats.last_updated_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
              : new Date().toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
            icon={<Clock className="h-5 w-5" />}
          />
        </div>
      ) : null}

      {/* Category Overview */}
      <div>
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">分类概览</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card hover className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <ShoppingBag className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-surface-500 dark:text-surface-400">服饰 Apparel</p>
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{catCounts.apparel}</p>
            </div>
          </Card>
          <Card hover className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
              <Footprints className="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-surface-500 dark:text-surface-400">鞋履 Footwear</p>
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{catCounts.footwear}</p>
            </div>
          </Card>
          <Card hover className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <Briefcase className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-surface-500 dark:text-surface-400">包袋 Bags</p>
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{catCounts.bags}</p>
            </div>
          </Card>
        </div>
      </div>

      {/* Recent Events */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">最近竞对动态</h2>
          <Link
            to="/events"
            className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            查看全部
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        {eventsLoading ? (
          <Skeleton variant="text" />
        ) : events.length === 0 ? (
          <EmptyState title="暂无动态" description="近期没有竞对动态记录" />
        ) : (
          <Card padding="none">
            <div className="divide-y divide-surface-100 dark:divide-surface-800">
              {events.map((event) => (
                <div key={event.id} className="flex items-start gap-4 px-5 py-4">
                  <div className="flex-shrink-0 w-20 text-xs text-surface-400 dark:text-surface-500 pt-0.5">
                    {event.event_date
                      ? new Date(event.event_date).toLocaleDateString('zh-CN', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : ''}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Link
                        to={`/brands/${event.brand_slug || event.brand_name?.toLowerCase().replace(/\s+/g, '-') || '#'}`}
                        className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
                      >
                        {event.brand_name}
                      </Link>
                      <Badge size="sm" variant="primary">
                        {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                      </Badge>
                    </div>
                    <p className="text-sm text-surface-700 dark:text-surface-300">{event.title}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Brand Quick Browse */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">品牌快速浏览</h2>
          <Link
            to="/brands"
            className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            查看全部品牌
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        {brandsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} variant="card" />
            ))}
          </div>
        ) : brands.length === 0 ? (
          <EmptyState title="暂无品牌" description="品牌数据尚未导入" />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {brands.map((brand) => (
              <BrandCardMini key={brand.id} brand={brand} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Compare Entry */}
      <div>
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">快速对比入口</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { tier: 'Luxury', label: '奢侈品牌对比', desc: 'Gucci, Balenciaga, Burberry 等' },
            { tier: 'Premium', label: '高端品牌对比', desc: 'Lululemon, Arc\'teryx, On 等' },
            { tier: 'Mid', label: '中端品牌对比', desc: 'Allbirds, New Balance, Cotopaxi 等' },
            { tier: 'Mass', label: '平价品牌对比', desc: 'Crocs, JanSport, Vans 等' },
          ].map((item) => (
            <Link key={item.tier} to={`/compare?tier=${item.tier}`}>
              <Card hover className="h-full">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-surface-900 dark:text-white">{item.label}</h3>
                    <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">{item.desc}</p>
                  </div>
                  <TrendingUp className="h-5 w-5 text-surface-300 dark:text-surface-600" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
