import { Article } from '../api/client';
import { ArticleCard } from './ArticleCard';

interface ArticleListProps {
  articles: Article[];
  loading: boolean;
  error: string | null;
  onBookmarkToggle: (id: number) => void;
  onGenerateSummary: (id: number) => Promise<string | null>;
  onViewDetail: (article: Article) => void;
}

export function ArticleList({
  articles,
  loading,
  error,
  onBookmarkToggle,
  onGenerateSummary,
  onViewDetail,
}: ArticleListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-3 text-gray-600">
          <svg
            className="animate-spin h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Loading articles...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">No articles found</p>
          <p className="text-sm">Try adjusting your filters or refresh to fetch new articles.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {articles.map((article) => (
        <ArticleCard
          key={article.id}
          article={article}
          onBookmarkToggle={onBookmarkToggle}
          onGenerateSummary={onGenerateSummary}
          onViewDetail={onViewDetail}
        />
      ))}
    </div>
  );
}
