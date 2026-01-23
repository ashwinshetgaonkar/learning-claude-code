import { useArticles } from '../hooks/useArticles';
import { ArticleList } from '../components/ArticleList';
import { Article } from '../api/client';

interface BookmarksProps {
  onViewDetail: (article: Article) => void;
}

export function Bookmarks({ onViewDetail }: BookmarksProps) {
  const {
    articles,
    loading,
    error,
    toggleBookmark,
    generateSummary,
  } = useArticles({ bookmarkedOnly: true });

  return (
    <div className="flex-1 flex flex-col">
      <header className="bg-white border-b border-gray-200 p-4">
        <h1 className="text-2xl font-bold text-gray-900">Bookmarked Articles</h1>
        <p className="text-gray-600 mt-1">
          {articles.length} article{articles.length !== 1 ? 's' : ''} saved
        </p>
      </header>

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
