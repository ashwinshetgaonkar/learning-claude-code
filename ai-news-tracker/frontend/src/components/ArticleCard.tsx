import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Article, getArticlePdfUrl, getArticleMarkdownUrl } from '../api/client';

interface ArticleCardProps {
  article: Article;
  onBookmarkToggle: (id: number) => void;
  onGenerateSummary: (id: number) => Promise<string | null>;
  onViewDetail: (article: Article) => void;
}

const SOURCE_ICONS: Record<string, string> = {
  arxiv: '📄',
  huggingface: '🤗',
  blog: '📰',
  aggregator: '📢',
};

const SOURCE_LABELS: Record<string, string> = {
  arxiv: 'arXiv',
  huggingface: 'HuggingFace',
  blog: 'Blog',
  aggregator: 'News',
};

export function ArticleCard({ article, onBookmarkToggle, onGenerateSummary, onViewDetail }: ArticleCardProps) {
  const [summarizing, setSummarizing] = useState(false);

  const handleSummarize = async () => {
    setSummarizing(true);
    await onGenerateSummary(article.id);
    setSummarizing(false);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: article.title,
        url: article.url,
      });
    } else {
      navigator.clipboard.writeText(article.url);
      alert('Link copied to clipboard!');
    }
  };

  const publishedAt = article.published_at
    ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
    : 'Unknown date';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <span>{SOURCE_ICONS[article.source] || '📄'}</span>
            <span className="font-medium">{SOURCE_LABELS[article.source] || article.source}</span>
            <span>•</span>
            {article.categories.slice(0, 2).map((cat) => (
              <span
                key={cat}
                className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs"
              >
                {cat}
              </span>
            ))}
            <span>•</span>
            <span>{publishedAt}</span>
          </div>

          <h3
            className="text-lg font-semibold text-gray-900 mb-2 cursor-pointer hover:text-blue-600"
            onClick={() => onViewDetail(article)}
          >
            {article.title}
          </h3>

          {article.authors && article.authors.length > 0 && (
            <p className="text-sm text-gray-600 mb-2">
              {article.authors.slice(0, 3).join(', ')}
              {article.authors.length > 3 && ` +${article.authors.length - 3} more`}
            </p>
          )}

          {article.summary ? (
            <p className="text-gray-700 text-sm mb-3 line-clamp-3">{article.summary}</p>
          ) : article.abstract ? (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">{article.abstract}</p>
          ) : null}

          <div className="flex flex-wrap items-center gap-2 mt-3">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Read More
            </a>

            <button
              onClick={() => onBookmarkToggle(article.id)}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                article.is_bookmarked
                  ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {article.is_bookmarked ? '★ Bookmarked' : '☆ Bookmark'}
            </button>

            {!article.summary && (
              <button
                onClick={handleSummarize}
                disabled={summarizing}
                className="px-3 py-1.5 text-sm bg-purple-100 text-purple-700 rounded-md hover:bg-purple-200 transition-colors disabled:opacity-50"
              >
                {summarizing ? 'Summarizing...' : '✨ Summarize'}
              </button>
            )}

            {article.pdf_url && (
              <a
                href={getArticlePdfUrl(article.id)}
                className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
              >
                📥 PDF
              </a>
            )}

            <a
              href={getArticleMarkdownUrl(article.id)}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              📝 Markdown
            </a>

            <button
              onClick={handleShare}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              🔗 Share
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
