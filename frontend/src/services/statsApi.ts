import api from './api'
import type { ApiResponse } from '../types/brand'

export interface StatsOverview {
  total_brands: number
  active_brands: number
  total_categories: number
  total_events: number
  total_financial_records: number
  data_sources_count: number
  events_this_month?: number
  last_updated_at?: string
}

export interface CategoryDistribution {
  name: string
  slug: string
  count: number
}

export async function getStatsOverview(): Promise<ApiResponse<StatsOverview>> {
  return api.get('/stats/overview') as Promise<ApiResponse<StatsOverview>>
}

export async function getCategoryDistribution(): Promise<ApiResponse<CategoryDistribution[]>> {
  return api.get('/stats/category-distribution') as Promise<ApiResponse<CategoryDistribution[]>>
}
