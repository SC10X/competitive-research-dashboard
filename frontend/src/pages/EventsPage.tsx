import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Calendar, ExternalLink, Filter, RefreshCw, Loader2, CheckCircle2, Clock, Globe, Quote } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { SearchInput } from '@/components/ui/SearchInput'
import { FilterDropdown } from '@/components/ui/FilterDropdown'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { getEvents, refreshEvents } from '@/services/eventApi'
import { getBrands } from '@/services/brandApi'
import { EVENT_TYPE_LABELS } from '@/types/brand'
import type { CompetitiveEvent, Brand } from '@/types/brand'

const IMPORTANCE_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  low: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
}

const IMPORTANCE_LABELS: Record<string, string> = {
  high: '重要',
  medium: '一般',
  low: '低',
}

export default function EventsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [selectedImportance, setSelectedImportance] = useState<string[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date | null>(null)
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null)

  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['events', 'list', selectedTypes, selectedBrands, selectedImportance, startDate, endDate],
    queryFn: async () => {
      const res = await getEvents({
        event_type: selectedTypes.length > 0 ? selectedTypes.join(',') : undefined,
        brand_id: selectedBrands.length > 0 ? Number(selectedBrands[0]) : undefined,
        importance: selectedImportance.length > 0 ? selectedImportance.join(',') : undefined,
        date_from: startDate || undefined,
        date_to: endDate || undefined,
        page_size: 100,
      })
      return res.data
    },
  })

  const { data: brandsData } = useQuery({
    queryKey: ['brands', 'all'],
    queryFn: async () => {
      const res = await getBrands({ page_size: 200 })
      return res.data
    },
  })

  const events = (eventsData?.items || []) as CompetitiveEvent[]
  const allBrands = (brandsData?.items || []) as Brand[]

  const eventTypeOptions = useMemo(() => {
    const types = new Set<string>()
    events.forEach((e) => {
      if (e.event_type) types.add(e.event_type)
    })
    return Array.from(types).map((t) => ({
      value: t,
      label: EVENT_TYPE_LABELS[t] || t,
    }))
  }, [events])

  const brandOptions = useMemo(() => {
    return allBrands.map((b) => ({ value: String(b.id), label: b.name }))
  }, [allBrands])

  const importanceOptions = [
    { value: 'high', label: '重要' },
    { value: 'medium', label: '一般' },
    { value: 'low', label: '低' },
  ]

  const filteredEvents = useMemo(() => {
    let filtered = events
    if (search) {
      const q = search.toLowerCase()
      filtered = filtered.filter(
        (e) =>
          e.title?.toLowerCase().includes(q) ||
          e.brand_name?.toLowerCase().includes(q) ||
          e.description?.toLowerCase().includes(q)
      )
    }
    return filtered
  }, [events, search])

  // Group events by date
  const groupedEvents = useMemo(() => {
    const groups: Record<string, CompetitiveEvent[]> = {}
    filteredEvents.forEach((event) => {
      if (!event.event_date) return
      const date = new Date(event.event_date).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
      if (!groups[date]) groups[date] = []
      groups[date].push(event)
    })
    return Object.entries(groups).sort((a, b) => {
      const aDate = new Date(a[1][0]?.event_date || a[0])
      const bDate = new Date(b[1][0]?.event_date || b[0])
      return bDate.getTime() - aDate.getTime()
    })
  }, [filteredEvents])

  const handleRefresh = async () => {
    setRefreshing(true)
    setRefreshMessage(null)
    try {
      const res = await refreshEvents(undefined, 8)
      if (res.success && res.data) {
        setLastRefreshedAt(new Date())
        const msg = res.data.message || `已新增 ${res.data.refreshed_count} 条最新动态`
        setRefreshMessage(msg)
        // Invalidate queries to refetch events
        await queryClient.invalidateQueries({ queryKey: ['events'] })
        // Auto-hide message after 6 seconds
        setTimeout(() => setRefreshMessage(null), 6000)
      }
    } catch (e) {
      setRefreshMessage('刷新失败，请稍后重试')
      setTimeout(() => setRefreshMessage(null), 6000)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">竞对动态</h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">
            追踪竞品品牌的最新动态和市场活动
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefreshedAt && (
            <span className="text-xs text-surface-400">
              上次刷新: {lastRefreshedAt.toLocaleTimeString('zh-CN')}
            </span>
          )}
          <Button
            variant="primary"
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            {refreshing ? '刷新中...' : '一键刷新'}
          </Button>
        </div>
      </div>

      {refreshMessage && (
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-sm">
          <CheckCircle2 className="h-4 w-4" />
          {refreshMessage}
        </div>
      )}

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap items-center gap-3">
          <FilterDropdown
            label="事件类型"
            options={eventTypeOptions}
            selected={selectedTypes}
            onChange={setSelectedTypes}
          />
          <FilterDropdown
            label="品牌"
            options={brandOptions}
            selected={selectedBrands}
            onChange={setSelectedBrands}
            searchable
          />
          <FilterDropdown
            label="重要性"
            options={importanceOptions}
            selected={selectedImportance}
            onChange={setSelectedImportance}
          />
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="rounded-lg border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 px-3 py-2 text-sm text-surface-900 dark:text-white"
              placeholder="开始日期"
            />
            <span className="text-surface-400">-</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="rounded-lg border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 px-3 py-2 text-sm text-surface-900 dark:text-white"
              placeholder="结束日期"
            />
          </div>
          <div className="flex-grow" />
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="搜索动态..."
            className="w-full sm:w-64"
          />
        </div>
      </Card>

      {/* Events Timeline */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="text" />
          ))}
        </div>
      ) : groupedEvents.length === 0 ? (
        <EmptyState
          title="暂无竞对动态"
          description="没有找到匹配的动态记录，请调整筛选条件"
        />
      ) : (
        <div className="space-y-8">
          {groupedEvents.map(([date, dayEvents]) => (
            <div key={date}>
              <div className="flex items-center gap-3 mb-4">
                <Calendar className="h-5 w-5 text-primary-500" />
                <h2 className="text-lg font-semibold text-surface-900 dark:text-white">{date}</h2>
                <span className="text-sm text-surface-400">{dayEvents.length} 条动态</span>
              </div>
              <div className="space-y-3 ml-8 border-l-2 border-surface-200 dark:border-surface-700 pl-6">
                {dayEvents.map((event) => (
                  <div key={event.id} className="relative">
                    <div className="absolute -left-[31px] top-3 w-3 h-3 rounded-full bg-primary-500 border-2 border-white dark:border-surface-950" />
                    <Card>
                      <div className="flex flex-col gap-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Link
                            to={`/brands/${event.brand_slug || event.brand_name?.toLowerCase().replace(/\s+/g, '-') || '#'}`}
                            className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
                          >
                            {event.brand_name}
                          </Link>
                          <Badge size="sm" variant="primary">
                            {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                          </Badge>
                          <span
                            className={`text-xs px-1.5 py-0.5 rounded-full ${IMPORTANCE_COLORS[event.importance] || ''}`}
                          >
                            {IMPORTANCE_LABELS[event.importance] || event.importance}
                          </span>
                          {/* 事件发生时间标签 */}
                          <span className="inline-flex items-center gap-1 text-xs text-surface-500 dark:text-surface-400 ml-auto">
                            <Clock className="h-3 w-3" />
                            {new Date(event.event_date).toLocaleDateString('zh-CN', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        </div>
                        <h3 className="font-semibold text-surface-900 dark:text-white">
                          {event.title}
                        </h3>
                        <p className="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">
                          {event.description}
                        </p>
                        {event.source_quote && (
                          <div className="flex gap-2 text-xs text-surface-400 dark:text-surface-500 bg-surface-50 dark:bg-surface-800/50 rounded-lg px-3 py-2 border-l-2 border-surface-200 dark:border-surface-700">
                            <Quote className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
                            <span className="italic">原文引用：{event.source_quote}</span>
                          </div>
                        )}
                        {event.source_url && (
                          <a
                            href={event.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 w-fit"
                          >
                            <Globe className="h-3 w-3" />
                            阅读原文 — {event.source_name}
                          </a>
                        )}
                      </div>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
