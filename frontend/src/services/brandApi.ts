import api from './api'
import type { Brand, ApiResponse, BrandDetail } from '../types/brand'
import type { PaginationParams } from '../types/api'

export interface BrandFilterParams extends PaginationParams {
  category?: string
  price_tier?: string
  country?: string
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface BrandListOut {
  items: Brand[]
  total: number
}

export async function getBrands(params: BrandFilterParams = {}): Promise<ApiResponse<BrandListOut>> {
  return api.get('/brands', { params }) as Promise<ApiResponse<BrandListOut>>
}

export async function getBrandDetail(slug: string): Promise<ApiResponse<BrandDetail>> {
  return api.get(`/brands/${slug}`) as Promise<ApiResponse<BrandDetail>>
}

export async function getBrandDimensions(slug: string): Promise<ApiResponse<Record<string, unknown>>> {
  return api.get(`/brands/${slug}/dimensions`) as Promise<ApiResponse<Record<string, unknown>>>
}

export async function getBrandDimension(
  slug: string,
  dimension: string,
): Promise<ApiResponse<Record<string, unknown>>> {
  return api.get(`/brands/${slug}/dimensions/${dimension}`) as Promise<ApiResponse<Record<string, unknown>>>
}
