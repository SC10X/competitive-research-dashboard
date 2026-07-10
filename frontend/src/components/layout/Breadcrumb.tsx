import { useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { ChevronRight, Home, type LucideIcon } from 'lucide-react';

const routeLabels: Record<string, string> = {
  brands: '品牌列表',
  compare: '多维对比',
  categories: '分类筛选',
  trends: '趋势分析',
  events: '竞对动态',
  'data-import': '数据管理',
};

interface Crumb {
  label: string;
  path: string;
  icon?: LucideIcon;
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function Breadcrumb() {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  const crumbs: Crumb[] = [
    { label: '首页', path: '/', icon: Home },
  ];

  pathSegments.forEach((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/');
    const label = routeLabels[segment] || capitalize(segment.replace(/-/g, ' '));
    crumbs.push({ label, path });
  });

  return (
    <nav className="flex items-center gap-1 text-sm">
      {crumbs.map((crumb, index) => (
        <span key={crumb.path} className="flex items-center gap-1">
          {index > 0 && (
            <ChevronRight className="w-4 h-4 text-surface-400 dark:text-surface-500 flex-shrink-0" />
          )}
          {index === crumbs.length - 1 ? (
            <span className="text-surface-900 dark:text-white font-medium">
              {crumb.label}
            </span>
          ) : (
            <Link
              to={crumb.path}
              className="text-surface-500 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors flex items-center gap-1"
            >
              {crumb.icon && <crumb.icon className="w-4 h-4" />}
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
