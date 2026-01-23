import { useState, useCallback } from 'react';
import { useArticles } from '../hooks/useArticles';
import { SearchBar } from '../components/SearchBar';
import { FilterBar } from '../components/FilterBar';
import { ArticleList } from '../components/ArticleList';
import { Article } from '../api/client';

interface HomeProps {
  onViewDetail: (article: Article) => void;
}

const SOURCES = ['arxiv', 'huggingface', 'blog', 'aggregator'];
const CATEGORIES = [
  'NLP',
  'Computer Vision',
  'Machine Learning',
  'Reinforcement Learning',
  'Generative AI',
  'AI Safety',
  'LLM',
  'Neural Networks',
];

export function Home({ onViewDetail }: HomeProps) {
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDays, setSelectedDays] = useState<number | null>(null);

  const {
    articles,
    loading,
    error,
    refresh,
    search,
    toggleBookmark,
    generateSummary,
  } = useArticles({
    source: selectedSource || undefined,
    category: selectedCategory || undefined,
    days: selectedDays || undefined,
  });

  const handleSearch = useCallback(
    (query: string) => {
      search(query);
    },
    [search]
  );

  return (
    <div className="flex-1 flex flex-col">
      <header className="bg-white border-b border-gray-200 p-4">
        <SearchBar onSearch={handleSearch} onRefresh={refresh} isLoading={loading} />
      </header>

      <FilterBar
        sources={SOURCES}
        categories={CATEGORIES}
        selectedSource={selectedSource}
        selectedCategory={selectedCategory}
        selectedDays={selectedDays}
        onSourceChange={setSelectedSource}
        onCategoryChange={setSelectedCategory}
        onDaysChange={setSelectedDays}
      />

      <main className="flex-1 p-4 overflow-y-auto">
        <ArticleList
          articles={articles}
          loading={loading}
          error={error}
          onBookmarkToggle={toggleBookmark}
          onGenerateSummary={generateSummary}
          onViewDetail={onViewDetail}
        />
      </main>
    </div>
  );
}
