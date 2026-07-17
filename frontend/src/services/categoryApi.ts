import api from './api'
import type { CategoryTreeNode, ApiResponse } from '../types/brand'

export async function getCategories(dimension?: string): Promise<ApiResponse<CategoryTreeNode[]>> {
  const params = dimension ? { dimension } : {}
  return api.get('/categories', { params }) as Promise<ApiResponse<CategoryTreeNode[]>>
}
