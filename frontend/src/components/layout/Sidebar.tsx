import { NavLink, useLocation } from 'react-router-dom';
import { useUIStore } from '../../store/uiStore';
import {
  LayoutDashboard,
  Building2,
  GitCompare,
  FolderTree,
  TrendingUp,
  Activity,
  Database,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
  X,
} from 'lucide-react';
import { useEffect } from 'react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '首页仪表盘' },
  { to: '/brands', icon: Building2, label: '品牌列表' },
  { to: '/compare', icon: GitCompare, label: '多维对比' },
  { to: '/categories', icon: FolderTree, label: '分类筛选' },
  { to: '/trends', icon: TrendingUp, label: '趋势分析' },
  { to: '/events', icon: Activity, label: '竞对动态' },
  { to: '/data-import', icon: Database, label: '数据管理' },
];

export default function Sidebar() {
  const { sidebarOpen, setSidebarOpen, darkMode, toggleDarkMode } = useUIStore();
  const location = useLocation();

  // Close sidebar on mobile when route changes
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname, setSidebarOpen]);

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64
          bg-white dark:bg-surface-900
          border-r border-surface-200 dark:border-surface-700
          transform transition-transform duration-300 ease-in-out
          flex flex-col
          lg:translate-x-0 lg:static lg:z-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-surface-200 dark:border-surface-700">
          <NavLink to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CI</span>
            </div>
            <span className="font-semibold text-lg text-surface-900 dark:text-white">
              CI Dashboard
            </span>
          </NavLink>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-md hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                    : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800'
                }`
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Dark mode toggle */}
        <div className="p-4 border-t border-surface-200 dark:border-surface-700">
          <button
            onClick={toggleDarkMode}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium
                       text-surface-600 dark:text-surface-400
                       hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          >
            {darkMode ? (
              <Sun className="w-5 h-5 flex-shrink-0" />
            ) : (
              <Moon className="w-5 h-5 flex-shrink-0" />
            )}
            <span>{darkMode ? '浅色模式' : '深色模式'}</span>
          </button>
        </div>
      </aside>
    </>
  );
}
