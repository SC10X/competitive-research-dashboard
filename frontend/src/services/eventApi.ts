import api from './api'
import type { CompetitiveEvent, ApiResponse } from '../types/brand'
import type { PaginationParams } from '../types/api'

export interface EventFilterParams extends PaginationParams {
  brand_id?: number
  brand_slug?: string
  event_type?: string
  importance?: string
  date_from?: string
  date_to?: string
  search?: string
}

export interface EventListOut {
  items: CompetitiveEvent[]
  total: number
}

export interface EventRefreshResult {
  refreshed_count: number
  new_events: CompetitiveEvent[]
  refreshed_at: string
  message?: string
}

export async function getEvents(params: EventFilterParams = {}): Promise<ApiResponse<EventListOut>> {
  return api.get('/events', { params }) as Promise<ApiResponse<EventListOut>>
}

export async function getEventTimeline(
  params: EventFilterParams = {},
): Promise<ApiResponse<CompetitiveEvent[]>> {
  return api.get('/events/timeline', { params }) as Promise<ApiResponse<CompetitiveEvent[]>>
}

export async function refreshEvents(
  brand_id?: number,
  count: number = 8,
): Promise<ApiResponse<EventRefreshResult>> {
  const params: Record<string, number | string> = { count }
  if (brand_id != null) params.brand_id = brand_id
  return api.post('/events/refresh', null, { params, timeout: 90000 }) as Promise<ApiResponse<EventRefreshResult>>
}
