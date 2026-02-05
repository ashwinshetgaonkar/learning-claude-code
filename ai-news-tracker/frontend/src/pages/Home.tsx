import { useState, useCallback, useRef } from 'react';
import { useArticles } from '../hooks/useArticles';
import { FilterBar } from '../components/FilterBar';
import { ArticleList } from '../components/ArticleList';
import { Article } from '../api/client';

interface HomeProps {
  onViewDetail: (article: Article) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

const SOURCES = ['arxiv', 'huggingface', 'blog', 'aggregator'];
const CATEGORIES = [
  'AI',
  'Machine Learning',
  'Generative AI',
  'Tech News',
  'Research',
  'Discussion',
  'Project',
];

export function Home({ onViewDetail, selectedCategory, onCategoryChange }: HomeProps) {
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedDays, setSelectedDays] = useState<number | null>(null);
  const mainRef = useRef<HTMLElement>(null);

  const {
    articles,
    loading,
    error,
    toggleBookmark,
    generateSummary,
    page,
    totalPages,
    setPage,
  } = useArticles({
    source: selectedSource || undefined,
    category: selectedCategory || undefined,
    days: selectedDays || undefined,
  });

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    mainRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [setPage]);

  return (
    <div className="flex-1 flex flex-col">
      <FilterBar
        sources={SOURCES}
        categories={CATEGORIES}
        selectedSource={selectedSource}
        selectedCategory={selectedCategory}
        selectedDays={selectedDays}
        onSourceChange={setSelectedSource}
        onCategoryChange={onCategoryChange}
        onDaysChange={setSelectedDays}
      />

      <main ref={mainRef} className="flex-1 p-4 overflow-y-auto">
        <ArticleList
          articles={articles}
          loading={loading}
          error={error}
          onBookmarkToggle={toggleBookmark}
          onGenerateSummary={generateSummary}
          onViewDetail={onViewDetail}
          currentPage={page}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </main>
    </div>
  );
}
