import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Brand } from '../../types/brand';
import BrandCardMini from './BrandCardMini';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useRef, useState, useEffect } from 'react';

interface RelatedBrandsProps {
  brands: Brand[];
  currentBrandId: number;
  title?: string;
}

export default function RelatedBrands({
  brands,
  currentBrandId,
  title = '相关竞品',
}: RelatedBrandsProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const filtered = useMemo(
    () => brands.filter((b) => b.id !== currentBrandId),
    [brands, currentBrandId]
  );

  const checkScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 0);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  };

  useEffect(() => {
    checkScroll();
    const el = scrollRef.current;
    if (el) {
      el.addEventListener('scroll', checkScroll, { passive: true });
      return () => el.removeEventListener('scroll', checkScroll);
    }
  }, [filtered]);

  const scroll = (direction: 'left' | 'right') => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = 300;
    el.scrollBy({ left: direction === 'left' ? -amount : amount, behavior: 'smooth' });
  };

  if (filtered.length === 0) {
    return null;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white">{title}</h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => scroll('left')}
            disabled={!canScrollLeft}
            className="p-1.5 rounded-lg text-surface-500 dark:text-surface-400
                       hover:bg-surface-100 dark:hover:bg-surface-800
                       disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => scroll('right')}
            disabled={!canScrollRight}
            className="p-1.5 rounded-lg text-surface-500 dark:text-surface-400
                       hover:bg-surface-100 dark:hover:bg-surface-800
                       disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto scrollbar-hide pb-1"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {filtered.map((brand) => (
          <div key={brand.id} className="flex-shrink-0 w-56">
            <BrandCardMini brand={brand} />
          </div>
        ))}
      </div>
    </div>
  );
}
