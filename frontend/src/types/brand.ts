export interface Brand {
  id: number
  name: string
  slug: string
  country: string
  founded_year: number | null
  parent_company: string | null
  headquarters: string | null
  logo_url: string | null
  website: string | null
  description: string | null
  is_active: boolean
  price_tier?: string | null
  instagram_followers?: number | null
  monthly_web_visits?: number | null
  categories?: CategoryInfo[]
}

export interface CategoryInfo {
  id: number
  name: string
  slug: string
  category_slug?: string
  is_primary: boolean
}

export interface BrandPositioning {
  price_tier: string
  brand_tone: string
  core_value_proposition: string
  usp: string
  brand_story: string
}

export interface PricingStrategy {
  id: number
  category_name: string
  price_range_min: number
  price_range_max: number
  avg_price: number
  discount_frequency: string
  typical_discount_pct: number
  has_membership: boolean
  membership_price: number | null
  membership_model: string | null
}

export interface TargetDemographics {
  age_range: string
  gender_skew: string
  income_level: string
  lifestyle_tags: string[]
  core_scenarios: string[]
}

export interface ProductStrategy {
  hero_products: string[]
  launch_cadence: string
  sku_count_estimate: number
  has_sustainable_line: boolean
  collab_strategy: string
  recent_collabs: string[]
  tech_innovations: string[]
  category_expansion: string[]
}

export interface ChannelStrategy {
  dtc_pct: number
  wholesale_pct: number
  own_stores_na: number
  retail_partners: string[]
  ecommerce_platforms: string[]
  international_markets: string[]
}

export interface SocialMediaMetrics {
  id: number
  platform: string
  followers: number
  engagement_rate: number
  avg_likes: number
  avg_comments: number
  post_frequency: string
  top_hashtags: string[]
  key_kols: string[]
}

export interface DigitalCapability {
  monthly_web_visits: number
  app_rating: number | null
  app_downloads: string | null
  has_personalization: boolean
  has_virtual_tryon: boolean
  has_community_feature: boolean
  has_membership_program: boolean
  membership_name: string | null
  ai_features: string[]
}

export interface FinancialPerformance {
  id: number
  fiscal_year: number
  revenue: number
  revenue_growth_pct: number
  gross_margin_pct: number
  na_revenue_pct: number
  is_estimated: boolean
}

export interface CustomerSentiment {
  id: number
  platform: string
  rating: number
  review_count: number
  positive_themes: string[]
  negative_themes: string[]
  nps_score: number | null
}

export interface CompetitiveEvent {
  id: number
  brand_id: number
  brand_name?: string
  event_type: string
  title: string
  description: string
  event_date: string
  source_url: string | null
  source_name: string | null
  source_quote: string | null
  importance: string
  tags: string[]
}

export interface BrandDetail extends Brand {
  positioning: BrandPositioning
  pricing: PricingStrategy[]
  demographics: TargetDemographics
  product_strategy: ProductStrategy
  channel_strategy: ChannelStrategy
  social_media: SocialMediaMetrics[]
  digital: DigitalCapability
  financials: FinancialPerformance[]
  sentiment: CustomerSentiment[]
  events: CompetitiveEvent[]
}

export interface CategoryTreeNode {
  id: number
  name: string
  slug: string
  level: number
  children: CategoryTreeNode[]
  brand_count: number
}

export interface ComparisonGroup {
  id: number
  name: string
  brand_ids: number[]
  created_at: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  pagination?: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
  meta?: Record<string, unknown>
}

// Event types mapping
export const EVENT_TYPE_LABELS: Record<string, string> = {
  product_launch: '产品发布',
  funding: '融资',
  mna: '并购',
  ipo: 'IPO',
  exec_change: '高管变动',
  partnership: '合作',
  campaign: '营销活动',
  store_opening: '开店',
  sustainability: '可持续发展',
  other: '其他',
}

// Price tier labels (matches backend seed data: Luxury, Premium, Mid, Mass)
export const PRICE_TIER_LABELS: Record<string, string> = {
  Luxury: '奢侈',
  Premium: '高端',
  Mid: '中端',
  Mass: '平价',
}

// Price tier colors (matches backend seed data)
export const PRICE_TIER_COLORS: Record<string, string> = {
  Luxury: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  Premium: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  Mid: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  Mass: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
}

export const CATEGORY_COLORS: Record<string, string> = {
  apparel: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  footwear: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  bags: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
}

export const IMPORTANCE_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  low: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
}
