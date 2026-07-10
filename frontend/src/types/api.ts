export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface BrandFilterParams extends PaginationParams {
  category_id?: string
  price_tier?: string
  country?: string
  search?: string
  sort?: string
  order?: 'asc' | 'desc'
}
