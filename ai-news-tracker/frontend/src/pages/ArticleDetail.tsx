import { useState } from 'react';
import { formatDistanceToNow, format } from 'date-fns';
import { Article, getArticlePdfUrl, getArticleMarkdownUrl, summarizeArticle, addBookmark, removeBookmark } from '../api/client';

interface ArticleDetailProps {
  article: Article;
  onClose: () => void;
  onUpdate: (article: Article) => void;
}

export function ArticleDetail({ article, onClose, onUpdate }: ArticleDetailProps) {
  const [summarizing, setSummarizing] = useState(false);
  const [localArticle, setLocalArticle] = useState(article);

  const handleSummarize = async () => {
    setSummarizing(true);
    try {
      const response = await summarizeArticle(localArticle.id);
      const updated = { ...localArticle, summary: response.summary };
      setLocalArticle(updated);
      onUpdate(updated);
    } catch (err) {
      console.error('Failed to summarize:', err);
    }
    setSummarizing(false);
  };

  const handleToggleBookmark = async () => {
    try {
      if (localArticle.is_bookmarked) {
        await removeBookmark(localArticle.id);
      } else {
        await addBookmark(localArticle.id);
      }
      const updated = { ...localArticle, is_bookmarked: !localArticle.is_bookmarked };
      setLocalArticle(updated);
      onUpdate(updated);
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({ title: localArticle.title, url: localArticle.url });
    } else {
      navigator.clipboard.writeText(localArticle.url);
      alert('Link copied to clipboard!');
    }
  };

  const publishedAt = localArticle.published_at
    ? format(new Date(localArticle.published_at), 'MMMM d, yyyy')
    : null;

  const timeAgo = localArticle.published_at
    ? formatDistanceToNow(new Date(localArticle.published_at), { addSuffix: true })
    : null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <header className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                  {localArticle.source}
                </span>
                {localArticle.categories.map((cat) => (
                  <span
                    key={cat}
                    className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full"
                  >
                    {cat}
                  </span>
                ))}
              </div>
              <h1 className="text-2xl font-bold text-gray-900">{localArticle.title}</h1>
              {localArticle.authors && localArticle.authors.length > 0 && (
                <p className="text-gray-600 mt-2">
                  By {localArticle.authors.join(', ')}
                </p>
              )}
              {publishedAt && (
                <p className="text-sm text-gray-500 mt-1">
                  {publishedAt} ({timeAgo})
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {localArticle.summary && (
            <div className="mb-6 p-4 bg-purple-50 rounded-lg">
              <h2 className="text-sm font-semibold text-purple-700 mb-2">AI Summary</h2>
              <p className="text-gray-800">{localArticle.summary}</p>
            </div>
          )}

          {localArticle.abstract && (
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Abstract
              </h2>
              <p className="text-gray-700 leading-relaxed">{localArticle.abstract}</p>
            </div>
          )}

          {localArticle.content && (
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Content
              </h2>
              <div
                className="prose prose-gray max-w-none"
                dangerouslySetInnerHTML={{ __html: localArticle.content }}
              />
            </div>
          )}
        </main>

        <footer className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex flex-wrap items-center gap-3">
            <a
              href={localArticle.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Open Original
            </a>

            <button
              onClick={handleToggleBookmark}
              className={`px-4 py-2 rounded-lg transition-colors ${
                localArticle.is_bookmarked
                  ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {localArticle.is_bookmarked ? '★ Bookmarked' : '☆ Bookmark'}
            </button>

            {!localArticle.summary && (
              <button
                onClick={handleSummarize}
                disabled={summarizing}
                className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors disabled:opacity-50"
              >
                {summarizing ? 'Summarizing...' : '✨ Generate Summary'}
              </button>
            )}

            {localArticle.pdf_url && (
              <a
                href={getArticlePdfUrl(localArticle.id)}
                className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
              >
                📥 Download PDF
              </a>
            )}

            <a
              href={getArticleMarkdownUrl(localArticle.id)}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              📝 Export Markdown
            </a>

            <button
              onClick={handleShare}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              🔗 Share
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
