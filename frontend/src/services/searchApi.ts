import api from './api'
import type { ApiResponse, Brand, CompetitiveEvent } from '../types/brand'

export type SearchType = 'brand' | 'event' | 'all'

export interface SearchResult {
  brands: Brand[]
  events: CompetitiveEvent[]
}

export async function search(q: string, type: SearchType = 'all'): Promise<ApiResponse<SearchResult>> {
  return api.get('/search', { params: { q, type } }) as Promise<ApiResponse<SearchResult>>
}
