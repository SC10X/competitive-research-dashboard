import { create } from 'zustand'

export interface TrendItem {
  id: number
  name: string
  slug: string
  price_tier?: string | null
}

interface TrendState {
  items: TrendItem[]
  maxItems: number
  addItem: (item: TrendItem) => void
  removeItem: (itemId: number) => void
  clearAll: () => void
  isSelected: (itemId: number) => boolean
}

export const useTrendStore = create<TrendState>()((set, get) => ({
  items: [],
  maxItems: 6,

  addItem: (item) => {
    const { items, maxItems } = get()
    if (items.length >= maxItems) return
    if (items.some((b) => b.id === item.id)) return
    set({ items: [...items, item] })
  },

  removeItem: (itemId) => {
    set({ items: get().items.filter((b) => b.id !== itemId) })
  },

  clearAll: () => {
    set({ items: [] })
  },

  isSelected: (itemId) => {
    return get().items.some((b) => b.id === itemId)
  },
}))
