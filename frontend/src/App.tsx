import { Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import MainLayout from '@/layouts/MainLayout'
import HomePage from '@/pages/HomePage'
import BrandListPage from '@/pages/BrandListPage'
import BrandDetailPage from '@/pages/BrandDetailPage'
import ComparePage from '@/pages/ComparePage'
import CategoriesPage from '@/pages/CategoriesPage'
import TrendsPage from '@/pages/TrendsPage'
import EventsPage from '@/pages/EventsPage'
import DataImportPage from '@/pages/DataImportPage'
import DataSourcesPage from '@/pages/DataSourcesPage'

function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <h1 className="text-6xl font-bold text-surface-200 dark:text-surface-700">404</h1>
      <p className="mt-4 text-lg text-surface-500 dark:text-surface-400">页面未找到</p>
    </div>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/brands" element={<BrandListPage />} />
          <Route path="/brands/:slug" element={<BrandDetailPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/categories/:slug" element={<CategoriesPage />} />
          <Route path="/trends" element={<TrendsPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/data-import" element={<DataImportPage />} />
          <Route path="/data-sources" element={<DataSourcesPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}
