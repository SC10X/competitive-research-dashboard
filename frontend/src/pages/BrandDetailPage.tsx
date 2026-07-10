import { useState, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Target,
  DollarSign,
  Users,
  Package,
  Store,
  Share2,
  Monitor,
  BarChart3,
  MessageSquare,
  Activity,
  TrendingUp,
  TrendingDown,
  ExternalLink,
  Star,
  ThumbsUp,
  ThumbsDown,
  Calendar,
  Globe,
  ShoppingBag,
  Smartphone,
  Award,
  Zap,
  Heart,
  MapPin,
  Building2,
} from 'lucide-react'
import { Tabs } from '@/components/ui/Tabs'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import BrandHero from '@/components/brand/BrandHero'
import RelatedBrands from '@/components/brand/RelatedBrands'
import { getBrandDetail, getBrands } from '@/services/brandApi'
import { getEvents } from '@/services/eventApi'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import {
  EVENT_TYPE_LABELS,
  PRICE_TIER_LABELS,
  IMPORTANCE_COLORS,
  type BrandDetail,
  type CompetitiveEvent,
  type Brand,
} from '@/types/brand'
import { formatNumber, formatCurrency, formatPct } from '@/utils/format'
import { PLATFORM_COLORS } from '@/utils/constants'

// ============================================================
// 品牌定位
// ============================================================
function PositioningCard({ brand }: { brand: BrandDetail }) {
  const p = brand.positioning
  return (
    <Card>
      <div className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">价格带</p>
            <Badge variant="primary" className="mt-1">
              {PRICE_TIER_LABELS[p?.price_tier] || p?.price_tier || '-'}
            </Badge>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">品牌调性</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {p?.brand_tone || '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">核心价值主张</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {p?.core_value_proposition || '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">独特卖点 (USP)</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {p?.usp || '-'}
            </p>
          </div>
        </div>
        {p?.brand_story && (
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">品牌故事</p>
            <p className="text-surface-700 dark:text-surface-300 leading-relaxed">
              {p.brand_story}
            </p>
          </div>
        )}
        {brand.description && (
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">品牌描述</p>
            <p className="text-surface-700 dark:text-surface-300 leading-relaxed">
              {brand.description}
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============================================================
// 价格策略
// ============================================================
function PricingCard({ brand }: { brand: BrandDetail }) {
  const pricing = brand.pricing || []

  if (pricing.length === 0) {
    return (
      <Card>
        <EmptyState title="暂无价格数据" description="该品牌暂无价格策略数据" />
      </Card>
    )
  }

  return (
    <Card>
      <p className="text-sm text-surface-500 dark:text-surface-400 mb-4">
        各品类价格区间与折扣策略
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-200 dark:border-surface-700">
              <th className="text-left py-3 font-medium text-surface-500 dark:text-surface-400">
                品类
              </th>
              <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                价格区间
              </th>
              <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                均价
              </th>
              <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                折扣频率
              </th>
              <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                折扣比例
              </th>
              <th className="text-center py-3 font-medium text-surface-500 dark:text-surface-400">
                会员制
              </th>
            </tr>
          </thead>
          <tbody>
            {pricing.map((item, i) => (
              <tr
                key={item.id || i}
                className="border-b border-surface-100 dark:border-surface-800"
              >
                <td className="py-3 text-surface-900 dark:text-white font-medium">
                  {item.category_name}
                </td>
                <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                  {formatCurrency(item.price_range_min)} - {formatCurrency(item.price_range_max)}
                </td>
                <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                  {formatCurrency(item.avg_price)}
                </td>
                <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                  {item.discount_frequency || '-'}
                </td>
                <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                  {item.typical_discount_pct != null ? `${item.typical_discount_pct}%` : '-'}
                </td>
                <td className="text-center py-3">
                  {item.has_membership ? (
                    <Badge variant="success" size="sm">是</Badge>
                  ) : (
                    <span className="text-surface-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

// ============================================================
// 目标人群
// ============================================================
function DemographicsCard({ brand }: { brand: BrandDetail }) {
  const d = brand.demographics

  return (
    <Card>
      <div className="space-y-5">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">目标年龄</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {d?.age_range || '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">性别倾向</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {d?.gender_skew || '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">收入水平</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {d?.income_level || '-'}
            </p>
          </div>
        </div>

        {d?.lifestyle_tags && d.lifestyle_tags.length > 0 && (
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">生活方式标签</p>
            <div className="flex flex-wrap gap-2">
              {d.lifestyle_tags.map((tag) => (
                <Badge key={tag} variant="neutral" size="sm">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {d?.core_scenarios && d.core_scenarios.length > 0 && (
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">核心场景</p>
            <div className="flex flex-wrap gap-2">
              {d.core_scenarios.map((scenario) => (
                <Badge key={scenario} variant="neutral" size="sm">
                  {scenario}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============================================================
// 产品策略
// ============================================================
function ProductStrategyCard({ brand }: { brand: BrandDetail }) {
  const ps = brand.product_strategy

  // Parse JSON fields if they're strings
  const heroProducts: Array<Record<string, unknown>> = typeof ps?.hero_products === 'string'
    ? JSON.parse(ps.hero_products as string)
    : (ps?.hero_products as any) || []
  const recentCollabs: Array<Record<string, unknown>> = typeof ps?.recent_collabs === 'string'
    ? JSON.parse(ps.recent_collabs as string)
    : (ps?.recent_collabs as any) || []
  const techInnovations: Array<Record<string, unknown>> = typeof ps?.tech_innovations === 'string'
    ? JSON.parse(ps.tech_innovations as string)
    : (ps?.tech_innovations as any) || []
  const categoryExpansion: string[] = typeof ps?.category_expansion === 'string'
    ? JSON.parse(ps.category_expansion as string)
    : (ps?.category_expansion as any) || []

  return (
    <Card>
      <div className="space-y-6">
        {/* Hero Products */}
        <div>
          <h3 className="font-medium text-surface-900 dark:text-white mb-3 flex items-center gap-2">
            <Award className="h-4 w-4 text-amber-500" />
            明星产品
          </h3>
          {heroProducts.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {heroProducts.map((product: any, i: number) => (
                <div
                  key={i}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-50 dark:bg-surface-800 text-sm"
                >
                  <Package className="h-4 w-4 text-surface-400 flex-shrink-0" />
                  <div>
                    <span className="text-surface-700 dark:text-surface-300 font-medium">{product.name || product}</span>
                    {product.price != null && (
                      <span className="text-surface-400 ml-2">${product.price}</span>
                    )}
                    {product.category && (
                      <span className="block text-xs text-surface-400">{product.category}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-surface-400">暂无数据</p>
          )}
        </div>

        {/* Product Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">上新节奏</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {ps?.launch_cadence || '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">SKU 估算</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {ps?.sku_count_estimate != null ? formatNumber(ps.sku_count_estimate) : '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">可持续产品线</p>
            <p className="text-surface-900 dark:text-white font-medium mt-1">
              {ps?.has_sustainable_line ? (
                <Badge variant="success" size="sm">有</Badge>
              ) : (
                <span className="text-surface-400">无</span>
              )}
            </p>
          </div>
        </div>

        {/* Collab Strategy */}
        <div>
          <h3 className="font-medium text-surface-900 dark:text-white mb-2 flex items-center gap-2">
            <Heart className="h-4 w-4 text-rose-500" />
            联名合作
          </h3>
          {recentCollabs.length > 0 ? (
            <div className="space-y-2">
              {recentCollabs.map((collab: any, i: number) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <Badge variant="primary" size="sm">
                    {collab.partner || collab}
                  </Badge>
                  {collab.type && (
                    <span className="text-surface-500 dark:text-surface-400 text-xs">{collab.type}</span>
                  )}
                  {collab.year && (
                    <span className="text-surface-400 text-xs ml-auto">{collab.year}</span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-surface-400">暂无数据</p>
          )}
          {ps?.collab_strategy && (
            <p className="text-sm text-surface-500 dark:text-surface-400 mt-2">
              {ps.collab_strategy}
            </p>
          )}
        </div>

        {/* Tech Innovations */}
        {techInnovations.length > 0 && (
          <div>
            <h3 className="font-medium text-surface-900 dark:text-white mb-2 flex items-center gap-2">
              <Zap className="h-4 w-4 text-blue-500" />
              技术创新
            </h3>
            <div className="space-y-2">
              {techInnovations.map((tech: any, i: number) => (
                <div
                  key={i}
                  className="flex items-start gap-3 px-3 py-2 rounded-lg bg-surface-50 dark:bg-surface-800"
                >
                  <Badge variant="success" size="sm" className="mt-0.5 flex-shrink-0">
                    {tech.name || tech}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    {tech.desc && (
                      <p className="text-sm text-surface-600 dark:text-surface-400">{tech.desc}</p>
                    )}
                  </div>
                  {tech.year && (
                    <span className="text-xs text-surface-400 flex-shrink-0">{tech.year}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category Expansion */}
        {categoryExpansion.length > 0 && (
          <div>
            <h3 className="font-medium text-surface-900 dark:text-white mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-500" />
              品类拓展
            </h3>
            <div className="flex flex-wrap gap-2">
              {categoryExpansion.map((cat, i) => (
                <Badge key={i} variant="neutral" size="sm">
                  {typeof cat === 'string' ? cat : (cat as any).name || String(cat)}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============================================================
// 渠道策略
// ============================================================
function ChannelStrategyCard({ brand }: { brand: BrandDetail }) {
  const cs = brand.channel_strategy

  const pieData = useMemo(() => {
    const dtc = cs?.dtc_pct ?? 0
    const wholesale = cs?.wholesale_pct ?? 0
    const other = Math.max(0, 100 - dtc - wholesale)
    return [
      { name: 'DTC', value: dtc },
      { name: '批发', value: wholesale },
      { name: '其他', value: other },
    ].filter((d) => d.value > 0)
  }, [cs])

  const PIE_COLORS = ['#6366f1', '#10b981', '#f59e0b']

  return (
    <Card>
      <div className="space-y-6">
        <div className="flex flex-col lg:flex-row items-center gap-6">
          {pieData.length > 0 && (
            <div className="w-52 h-52 flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`${value}%`, '占比']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="flex-1 space-y-4 w-full">
            <h3 className="font-medium text-surface-900 dark:text-white flex items-center gap-2">
              <Store className="h-4 w-4" />
              渠道详情
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <p className="text-sm text-surface-400 dark:text-surface-500">北美自营门店</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">
                  {cs?.own_stores_na != null ? cs.own_stores_na : '-'}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <p className="text-sm text-surface-400 dark:text-surface-500">DTC 占比</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">
                  {cs?.dtc_pct != null ? `${cs.dtc_pct}%` : '-'}
                </p>
              </div>
            </div>

            {cs?.retail_partners && cs.retail_partners.length > 0 && (
              <div>
                <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">零售伙伴</p>
                <div className="flex flex-wrap gap-2">
                  {cs.retail_partners.map((partner) => (
                    <Badge key={partner} variant="neutral" size="sm">
                      {partner}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {cs?.ecommerce_platforms && cs.ecommerce_platforms.length > 0 && (
              <div>
                <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">电商平台</p>
                <div className="flex flex-wrap gap-2">
                  {cs.ecommerce_platforms.map((platform) => (
                    <Badge key={platform} variant="primary" size="sm">
                      <ShoppingBag className="h-3 w-3 mr-1" />
                      {platform}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {cs?.international_markets && cs.international_markets.length > 0 && (
              <div>
                <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">国际市场</p>
                <div className="flex flex-wrap gap-2">
                  {cs.international_markets.map((market) => (
                    <Badge key={market} variant="neutral" size="sm">
                      <Globe className="h-3 w-3 mr-1" />
                      {market}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}

// ============================================================
// 社媒影响力
// ============================================================
function SocialMediaCard({ brand }: { brand: BrandDetail }) {
  const socialMedia = brand.social_media || []

  const platformData = useMemo(() => {
    return socialMedia.map((sm) => ({
      name: sm.platform,
      followers: sm.followers,
      fill: PLATFORM_COLORS[sm.platform] || '#6b7280',
    }))
  }, [socialMedia])

  if (socialMedia.length === 0) {
    return (
      <Card>
        <EmptyState title="暂无社媒数据" description="该品牌暂无社媒影响力数据" />
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {socialMedia.map((sm) => (
          <Card key={sm.id || sm.platform}>
            <div className="flex items-center gap-3">
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                style={{
                  backgroundColor: PLATFORM_COLORS[sm.platform] || '#6b7280',
                }}
              >
                {sm.platform.charAt(0)}
              </div>
              <div className="min-w-0">
                <p className="text-sm text-surface-500 dark:text-surface-400">{sm.platform}</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">
                  {formatNumber(sm.followers)}
                </p>
                <div className="flex items-center gap-3 mt-1 text-xs text-surface-400">
                  <span>互动率 {sm.engagement_rate}%</span>
                  <span>均赞 {formatNumber(sm.avg_likes)}</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Bar Chart: 平台 vs 粉丝数 */}
      {platformData.length > 0 && (
        <Card>
          <h3 className="font-medium text-surface-900 dark:text-white mb-4">粉丝数对比</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={platformData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatNumber(v)} />
                <Tooltip formatter={(value: number) => [formatNumber(value), '粉丝数']} />
                <Bar dataKey="followers" radius={[6, 6, 0, 0]} maxBarSize={80}>
                  {platformData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </div>
  )
}

// ============================================================
// 数字化能力
// ============================================================
function DigitalCard({ brand }: { brand: BrandDetail }) {
  const dig = brand.digital

  return (
    <Card>
      <div className="space-y-5">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">月访问量</p>
            <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
              {dig?.monthly_web_visits ? formatNumber(dig.monthly_web_visits) : '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">App 评分</p>
            <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
              {dig?.app_rating != null ? (
                <>
                  <Star className="h-5 w-5 inline text-amber-400 mr-1" />
                  {dig.app_rating}
                </>
              ) : (
                '-'
              )}
            </p>
          </div>
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500">App 下载量</p>
            <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
              {dig?.app_downloads || '-'}
            </p>
          </div>
        </div>

        {/* Feature Flags */}
        <div>
          <p className="text-sm text-surface-400 dark:text-surface-500 mb-3">数字能力</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
              <Smartphone className="h-4 w-4 text-surface-400" />
              <div>
                <p className="text-xs text-surface-400">个性化推荐</p>
                <Badge variant={dig?.has_personalization ? 'success' : 'neutral'} size="sm">
                  {dig?.has_personalization ? '支持' : '不支持'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
              <Smartphone className="h-4 w-4 text-surface-400" />
              <div>
                <p className="text-xs text-surface-400">虚拟试穿</p>
                <Badge variant={dig?.has_virtual_tryon ? 'success' : 'neutral'} size="sm">
                  {dig?.has_virtual_tryon ? '支持' : '不支持'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
              <Users className="h-4 w-4 text-surface-400" />
              <div>
                <p className="text-xs text-surface-400">社区功能</p>
                <Badge variant={dig?.has_community_feature ? 'success' : 'neutral'} size="sm">
                  {dig?.has_community_feature ? '支持' : '不支持'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
              <Award className="h-4 w-4 text-surface-400" />
              <div>
                <p className="text-xs text-surface-400">会员计划</p>
                <Badge variant={dig?.has_membership_program ? 'success' : 'neutral'} size="sm">
                  {dig?.has_membership_program ? '支持' : '不支持'}
                </Badge>
              </div>
            </div>
          </div>
          {dig?.has_membership_program && dig?.membership_name && (
            <p className="text-sm text-surface-500 dark:text-surface-400 mt-2">
              会员名称: {dig.membership_name}
            </p>
          )}
        </div>

        {/* AI Features */}
        {dig?.ai_features && dig.ai_features.length > 0 && (
          <div>
            <p className="text-sm text-surface-400 dark:text-surface-500 mb-2">AI 功能</p>
            <div className="flex flex-wrap gap-2">
              {dig.ai_features.map((feature, i) => (
                <Badge key={i} variant="primary" size="sm">
                  {feature}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============================================================
// 财务表现
// ============================================================
function FinancialsCard({ brand }: { brand: BrandDetail }) {
  const financials = brand.financials || []

  const chartData = useMemo(() => {
    return [...financials]
      .sort((a, b) => a.fiscal_year - b.fiscal_year)
      .map((f) => ({
        year: f.fiscal_year,
        revenue: f.revenue,
        growth: f.revenue_growth_pct,
      }))
  }, [financials])

  if (financials.length === 0) {
    return (
      <Card>
        <EmptyState title="暂无财务数据" description="该品牌暂无财务表现数据" />
      </Card>
    )
  }

  // Latest year data
  const latest = financials.reduce((prev, curr) =>
    curr.fiscal_year > prev.fiscal_year ? curr : prev
  )

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm text-surface-400 dark:text-surface-500">最新营收</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
            {formatCurrency(latest.revenue)}
          </p>
          <p className="text-xs text-surface-400 mt-1">FY{latest.fiscal_year}</p>
        </Card>
        <Card>
          <p className="text-sm text-surface-400 dark:text-surface-500">营收增长</p>
          <div className="flex items-center gap-1 mt-1">
            {latest.revenue_growth_pct >= 0 ? (
              <TrendingUp className="h-5 w-5 text-green-500" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-500" />
            )}
            <p
              className={`text-2xl font-bold ${
                latest.revenue_growth_pct >= 0
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'
              }`}
            >
              {formatPct(latest.revenue_growth_pct)}
            </p>
          </div>
          <p className="text-xs text-surface-400 mt-1">FY{latest.fiscal_year}</p>
        </Card>
        <Card>
          <p className="text-sm text-surface-400 dark:text-surface-500">毛利率</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
            {latest.gross_margin_pct != null ? `${latest.gross_margin_pct}%` : '-'}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-surface-400 dark:text-surface-500">北美营收占比</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white mt-1">
            {latest.na_revenue_pct != null ? `${latest.na_revenue_pct}%` : '-'}
          </p>
        </Card>
      </div>

      {/* Revenue Line Chart */}
      {chartData.length > 0 && (
        <Card>
          <h3 className="font-medium text-surface-900 dark:text-white mb-4">营收趋势</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatCurrency(v)} />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    name === 'revenue' ? formatCurrency(value) : `${value}%`,
                    name === 'revenue' ? '营收' : '增长率',
                  ]}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={{ r: 4, fill: '#6366f1' }}
                  name="营收"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Financial Details Table */}
      <Card>
        <h3 className="font-medium text-surface-900 dark:text-white mb-4">历年财务数据</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-200 dark:border-surface-700">
                <th className="text-left py-3 font-medium text-surface-500 dark:text-surface-400">
                  财年
                </th>
                <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                  营收
                </th>
                <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                  增长率
                </th>
                <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                  毛利率
                </th>
                <th className="text-right py-3 font-medium text-surface-500 dark:text-surface-400">
                  北美占比
                </th>
                <th className="text-center py-3 font-medium text-surface-500 dark:text-surface-400">
                  估算
                </th>
              </tr>
            </thead>
            <tbody>
              {[...financials]
                .sort((a, b) => b.fiscal_year - a.fiscal_year)
                .map((f) => (
                  <tr
                    key={f.id}
                    className="border-b border-surface-100 dark:border-surface-800"
                  >
                    <td className="py-3 text-surface-900 dark:text-white font-medium">
                      FY{f.fiscal_year}
                    </td>
                    <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                      {formatCurrency(f.revenue)}
                    </td>
                    <td
                      className={`text-right py-3 ${
                        f.revenue_growth_pct >= 0
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-600 dark:text-red-400'
                      }`}
                    >
                      {formatPct(f.revenue_growth_pct)}
                    </td>
                    <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                      {f.gross_margin_pct}%
                    </td>
                    <td className="text-right py-3 text-surface-600 dark:text-surface-400">
                      {f.na_revenue_pct}%
                    </td>
                    <td className="text-center py-3">
                      {f.is_estimated ? (
                        <Badge variant="neutral" size="sm">估算</Badge>
                      ) : (
                        <span className="text-surface-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

// ============================================================
// 用户口碑
// ============================================================
function SentimentCard({ brand }: { brand: BrandDetail }) {
  const sentiment = brand.sentiment || []

  if (sentiment.length === 0) {
    return (
      <Card>
        <EmptyState title="暂无口碑数据" description="该品牌暂无用户口碑数据" />
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Platform Ratings */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {sentiment.map((s) => (
          <Card key={s.id || s.platform}>
            <div className="flex items-center gap-3 mb-3">
              <Star className="h-5 w-5 text-amber-400" />
              <span className="font-medium text-surface-900 dark:text-white">{s.platform}</span>
            </div>
            <p className="text-3xl font-bold text-surface-900 dark:text-white">
              {s.rating}
              <span className="text-lg text-surface-400 font-normal"> / 5.0</span>
            </p>
            <p className="text-sm text-surface-400 mt-1">
              {formatNumber(s.review_count)} 条评价
              {s.nps_score != null && ` · NPS ${s.nps_score}`}
            </p>
          </Card>
        ))}
      </div>

      {/* Themes */}
      {sentiment.map((s) => (
        <div key={`themes-${s.id || s.platform}`} className="space-y-4">
          {s.positive_themes && s.positive_themes.length > 0 && (
            <Card>
              <h3 className="font-medium text-surface-900 dark:text-white mb-3 flex items-center gap-2">
                <ThumbsUp className="h-4 w-4 text-green-500" />
                正面主题 ({s.platform})
              </h3>
              <div className="flex flex-wrap gap-2">
                {s.positive_themes.map((theme) => (
                  <Badge key={theme} variant="success" size="sm">
                    {theme}
                  </Badge>
                ))}
              </div>
            </Card>
          )}
          {s.negative_themes && s.negative_themes.length > 0 && (
            <Card>
              <h3 className="font-medium text-surface-900 dark:text-white mb-3 flex items-center gap-2">
                <ThumbsDown className="h-4 w-4 text-red-500" />
                负面主题 ({s.platform})
              </h3>
              <div className="flex flex-wrap gap-2">
                {s.negative_themes.map((theme) => (
                  <Badge key={theme} variant="danger" size="sm">
                    {theme}
                  </Badge>
                ))}
              </div>
            </Card>
          )}
        </div>
      ))}
    </div>
  )
}

// ============================================================
// 竞对动态
// ============================================================
function EventsTab({ brand }: { brand: BrandDetail }) {
  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['events', 'brand', brand.id],
    queryFn: async () => {
      const res = await getEvents({ brand_id: brand.id, page_size: 20 })
      return res.data
    },
  })

  const events: CompetitiveEvent[] = useMemo(() => {
    const items = Array.isArray(eventsData) ? eventsData : (eventsData as any)?.items || []
    return items as CompetitiveEvent[]
  }, [eventsData])

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton variant="card" />
        <Skeleton variant="card" />
        <Skeleton variant="card" />
      </div>
    )
  }

  if (events.length === 0) {
    return <EmptyState title="暂无竞对动态" description="该品牌近期没有竞对动态" />
  }

  return (
    <div className="space-y-4">
      {events.map((event) => (
        <Card key={event.id}>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-20 text-xs text-surface-400 dark:text-surface-500 pt-0.5">
              <Calendar className="h-3.5 w-3.5 inline mr-1" />
              {event.event_date
                ? new Date(event.event_date).toLocaleDateString('zh-CN')
                : ''}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <Badge size="sm" variant="primary">
                  {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                </Badge>
                {event.importance && (
                  <Badge
                    size="sm"
                    className={IMPORTANCE_COLORS[event.importance] || ''}
                  >
                    {event.importance === 'high' ? '高重要' : event.importance === 'medium' ? '中重要' : '低重要'}
                  </Badge>
                )}
                {event.brand_name && (
                  <span className="text-xs text-surface-400">{event.brand_name}</span>
                )}
              </div>
              <p className="font-medium text-surface-900 dark:text-white">{event.title}</p>
              {event.description && (
                <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
                  {event.description}
                </p>
              )}
              {event.source_url && (
                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 mt-2"
                >
                  <ExternalLink className="h-3 w-3" />
                  查看来源
                </a>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

// ============================================================
// 品牌详情页面主体
// ============================================================
export default function BrandDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const [activeTab, setActiveTab] = useState('positioning')

  // Fetch brand detail
  const {
    data: brandData,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['brand', slug],
    queryFn: async () => {
      const res = await getBrandDetail(slug!)
      return res.data
    },
    enabled: !!slug,
  })

  // Fetch all brands for related brands
  const { data: allBrands } = useQuery({
    queryKey: ['brands', 'all'],
    queryFn: async () => {
      const res = await getBrands({ page_size: 100 })
      return res.data
    },
  })

  const brand = brandData as BrandDetail | undefined
  const relatedBrands: Brand[] = Array.isArray(allBrands) ? allBrands : ((allBrands as any)?.items || []) as Brand[]

  const tabs = [
    { key: 'positioning', label: '品牌定位', icon: Target },
    { key: 'pricing', label: '价格策略', icon: DollarSign },
    { key: 'demographics', label: '目标人群', icon: Users },
    { key: 'product_strategy', label: '产品策略', icon: Package },
    { key: 'channel_strategy', label: '渠道策略', icon: Store },
    { key: 'social_media', label: '社媒影响力', icon: Share2 },
    { key: 'digital', label: '数字化能力', icon: Monitor },
    { key: 'financials', label: '财务表现', icon: BarChart3 },
    { key: 'sentiment', label: '用户口碑', icon: MessageSquare },
    { key: 'events', label: '竞对动态', icon: Activity },
  ]

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 p-4">
        <Skeleton variant="card" className="h-48" />
        <div className="flex gap-2 overflow-x-auto pb-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="h-9 w-24 animate-pulse rounded-lg bg-surface-200 dark:bg-surface-700 flex-shrink-0"
            />
          ))}
        </div>
        <Skeleton variant="card" />
        <Skeleton variant="chart" />
        <Skeleton variant="text" />
      </div>
    )
  }

  // Error / slug invalid
  if (isError || !brand) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <EmptyState
          title="品牌未找到"
          description="该品牌不存在或已被删除，请检查链接是否正确"
        />
      </div>
    )
  }

  const tabItems = tabs.map((t) => ({
    key: t.key,
    label: (
      <span className="flex items-center gap-1.5 whitespace-nowrap">
        <t.icon className="h-4 w-4" />
        <span className="hidden sm:inline">{t.label}</span>
      </span>
    ),
  }))

  const renderTabContent = () => {
    switch (activeTab) {
      case 'positioning':
        return <PositioningCard brand={brand} />
      case 'pricing':
        return <PricingCard brand={brand} />
      case 'demographics':
        return <DemographicsCard brand={brand} />
      case 'product_strategy':
        return <ProductStrategyCard brand={brand} />
      case 'channel_strategy':
        return <ChannelStrategyCard brand={brand} />
      case 'social_media':
        return <SocialMediaCard brand={brand} />
      case 'digital':
        return <DigitalCard brand={brand} />
      case 'financials':
        return <FinancialsCard brand={brand} />
      case 'sentiment':
        return <SentimentCard brand={brand} />
      case 'events':
        return <EventsTab brand={brand} />
      default:
        return null
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-4">
      {/* Hero */}
      <BrandHero brand={brand} />

      {/* Tabs */}
      <Tabs
        tabs={tabItems}
        activeKey={activeTab}
        onChange={setActiveTab}
        className="overflow-x-auto"
      />

      {/* Tab Content */}
      <div className="mt-6">{renderTabContent()}</div>

      {/* Related Brands */}
      {brand.id && relatedBrands.length > 1 && (
        <RelatedBrands brands={relatedBrands} currentBrandId={brand.id} />
      )}
    </div>
  )
}
