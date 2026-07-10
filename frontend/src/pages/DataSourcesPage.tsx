import { useState } from 'react'
import {
  Database,
  Globe,
  FileText,
  RefreshCw,
  ExternalLink,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface DataSource {
  id: number
  name: string
  type: 'api' | 'file' | 'crawl'
  status: 'active' | 'inactive' | 'error'
  lastSync: string
  description: string
}

const mockSources: DataSource[] = [
  {
    id: 1,
    name: 'Brand Financial Reports API',
    type: 'api',
    status: 'active',
    lastSync: '2024-03-15 14:30',
    description: '上市公司财报数据接口',
  },
  {
    id: 2,
    name: 'Social Media Analytics',
    type: 'api',
    status: 'active',
    lastSync: '2024-03-15 12:00',
    description: 'Instagram/TikTok/YouTube 社媒数据',
  },
  {
    id: 3,
    name: 'Web Traffic Scraper',
    type: 'crawl',
    status: 'error',
    lastSync: '2024-03-10 08:00',
    description: 'SimilarWeb 流量数据抓取',
  },
]

const statusConfig = {
  active: {
    icon: CheckCircle,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    label: '运行中',
  },
  inactive: {
    icon: Clock,
    color: 'text-surface-400',
    bg: 'bg-surface-100 text-surface-700 dark:bg-surface-800 dark:text-surface-300',
    label: '已停用',
  },
  error: {
    icon: AlertCircle,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    label: '异常',
  },
}

const typeIcons = {
  api: Globe,
  file: FileText,
  crawl: Database,
}

const typeLabels = {
  api: 'API 接口',
  file: '文件导入',
  crawl: '数据抓取',
}

export default function DataSourcesPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">数据源管理</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          管理和监控数据来源
        </p>
      </div>

      {/* Coming Soon Banner */}
      <Card className="border-primary-200 bg-primary-50 dark:border-primary-800 dark:bg-primary-900/20">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-xl bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
            <Database className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-primary-800 dark:text-primary-300">
              数据源管理功能即将上线
            </h2>
            <p className="text-sm text-primary-600 dark:text-primary-400 mt-1">
              此页面将支持添加、配置和监控各类数据源，包括 API 接口、文件导入和网页抓取等。
            </p>
            <div className="flex flex-wrap gap-3 mt-4">
              <Badge variant="primary">API 数据源</Badge>
              <Badge variant="primary">定时同步</Badge>
              <Badge variant="primary">数据质量监控</Badge>
              <Badge variant="primary">异常告警</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Current Sources */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">
            当前数据源
          </h2>
          <Button variant="outline" size="sm" disabled>
            <RefreshCw className="h-4 w-4" />
            同步全部
          </Button>
        </div>

        <div className="space-y-3">
          {mockSources.map((source) => {
            const status = statusConfig[source.status]
            const StatusIcon = status.icon
            const TypeIcon = typeIcons[source.type]

            return (
              <Card key={source.id} hover>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="h-10 w-10 rounded-lg bg-surface-100 dark:bg-surface-800 flex items-center justify-center flex-shrink-0">
                      <TypeIcon className="h-5 w-5 text-surface-500 dark:text-surface-400" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-surface-900 dark:text-white">
                          {source.name}
                        </h3>
                        <Badge size="sm" className={status.bg}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {status.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-surface-500 dark:text-surface-400">
                        {source.description}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-surface-400">
                        <span className="flex items-center gap-1">
                          <Badge variant="neutral" size="sm">
                            {typeLabels[source.type]}
                          </Badge>
                        </span>
                        <span>最近同步: {source.lastSync}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" disabled>
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Placeholder Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h3 className="font-medium text-surface-900 dark:text-white">同步状态</h3>
              <p className="text-sm text-surface-500 dark:text-surface-400">
                2 个数据源正常，1 个异常
              </p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="font-medium text-surface-900 dark:text-white">数据质量</h3>
              <p className="text-sm text-surface-500 dark:text-surface-400">
                最新同步数据完整率 98.5%
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
