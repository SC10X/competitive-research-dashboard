import api from './api'
import type { ComparisonGroup, ApiResponse } from '../types/brand'

export interface CompareResult {
  brand_slugs: string[]
  dimensions: string[]
  data: Array<{
    brand_slug: string
    brand_name: string
    dimension: string
    data: Record<string, unknown> | Array<Record<string, unknown>>
  }>
}

export async function queryCompare(
  brandSlugs: string[],
  dimensions: string[],
): Promise<ApiResponse<CompareResult>> {
  return api.post('/compare/query', {
    brand_slugs: brandSlugs,
    dimensions,
  }) as Promise<ApiResponse<CompareResult>>
}

export async function getComparisonGroups(): Promise<ApiResponse<ComparisonGroup[]>> {
  return api.get('/compare') as Promise<ApiResponse<ComparisonGroup[]>>
}

export async function createComparisonGroup(
  name: string,
  brandIds: number[],
): Promise<ApiResponse<ComparisonGroup>> {
  return api.post('/compare', { name, brand_ids: brandIds }) as Promise<ApiResponse<ComparisonGroup>>
}

export async function deleteComparisonGroup(id: number): Promise<ApiResponse<null>> {
  return api.delete(`/compare/${id}`) as Promise<ApiResponse<null>>
}
