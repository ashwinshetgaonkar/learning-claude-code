import { useState, useEffect, useCallback } from 'react';
import {
  Article,
  fetchArticles,
  searchArticles,
  fetchBookmarks,
  addBookmark,
  removeBookmark,
  refreshAllSources,
  summarizeArticle,
} from '../api/client';

interface UseArticlesOptions {
  source?: string;
  category?: string;
  days?: number;
  bookmarkedOnly?: boolean;
}

export function useArticles(options: UseArticlesOptions = {}) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadArticles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (options.bookmarkedOnly) {
        const response = await fetchBookmarks();
        setArticles(response.bookmarks);
      } else {
        const response = await fetchArticles({
          source: options.source,
          category: options.category,
          days: options.days,
        });
        setArticles(response.articles);
      }
    } catch (err) {
      setError('Failed to load articles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [options.source, options.category, options.days, options.bookmarkedOnly]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  const search = async (query: string) => {
    if (!query.trim()) {
      loadArticles();
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await searchArticles(query);
      setArticles(response.articles);
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      await refreshAllSources();
      await loadArticles();
    } catch (err) {
      setError('Refresh failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleBookmark = async (articleId: number) => {
    const article = articles.find((a) => a.id === articleId);
    if (!article) return;

    try {
      if (article.is_bookmarked) {
        await removeBookmark(articleId);
      } else {
        await addBookmark(articleId);
      }
      setArticles((prev) =>
        prev.map((a) =>
          a.id === articleId ? { ...a, is_bookmarked: !a.is_bookmarked } : a
        )
      );
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    }
  };

  const generateSummary = async (articleId: number) => {
    try {
      const response = await summarizeArticle(articleId);
      setArticles((prev) =>
        prev.map((a) =>
          a.id === articleId ? { ...a, summary: response.summary } : a
        )
      );
      return response.summary;
    } catch (err) {
      console.error('Failed to generate summary:', err);
      return null;
    }
  };

  return {
    articles,
    loading,
    error,
    refresh,
    search,
    toggleBookmark,
    generateSummary,
    reload: loadArticles,
  };
}
