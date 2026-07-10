import api from './api'
import type { CategoryTreeNode, ApiResponse } from '../types/brand'

export async function getCategories(): Promise<ApiResponse<CategoryTreeNode[]>> {
  return api.get('/categories') as Promise<ApiResponse<CategoryTreeNode[]>>
}
