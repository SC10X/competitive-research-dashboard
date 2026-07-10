import api from './api'
import type { ApiResponse } from '../types/brand'

export interface RevenueTrendPoint {
  brand_id: number
  brand_name: string
  brand_slug: string
  fiscal_year: number
  revenue: number | null
  revenue_growth_pct: number | null
}

export interface TrendOverview {
  total_brands: number
  total_categories: number
  avg_revenue_growth: number | null
  top_revenue_brands: Array<{ name: string; slug: string; revenue: number; fiscal_year: number }>
  top_engagement_brands: Array<{ name: string; slug: string; platform: string; engagement_rate: number }>
}

export async function getRevenueTrend(
  brandSlugs: string[],
): Promise<ApiResponse<RevenueTrendPoint[]>> {
  return api.get('/trends/revenue', {
    params: { brand_slugs: brandSlugs.join(',') },
  }) as Promise<ApiResponse<RevenueTrendPoint[]>>
}

export async function getTrendOverview(): Promise<ApiResponse<TrendOverview>> {
  return api.get('/trends/overview') as Promise<ApiResponse<TrendOverview>>
}
