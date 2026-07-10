import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface CompareItem {
  id: number
  name: string
  slug: string
  price_tier?: string | null
  logo_url?: string | null
}

interface CompareState {
  items: CompareItem[]
  maxItems: number
  addItem: (item: CompareItem) => void
  removeItem: (itemId: number) => void
  clearAll: () => void
  isInBasket: (itemId: number) => boolean
}

export const useCompareStore = create<CompareState>()(
  persist(
    (set, get) => ({
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

      isInBasket: (itemId) => {
        return get().items.some((b) => b.id === itemId)
      },
    }),
    {
      name: 'compare-basket',
    }
  )
)
