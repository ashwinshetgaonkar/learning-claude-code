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

const ITEMS_PER_PAGE = 10;

export function useArticles(options: UseArticlesOptions = {}) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadArticles = useCallback(async (pageNum: number = 1) => {
    setLoading(true);
    setError(null);
    try {
      if (options.bookmarkedOnly) {
        const response = await fetchBookmarks();
        setArticles(response.bookmarks);
        setTotalPages(1);
      } else {
        const offset = (pageNum - 1) * ITEMS_PER_PAGE;
        const response = await fetchArticles({
          source: options.source,
          category: options.category,
          days: options.days,
          limit: ITEMS_PER_PAGE,
          offset,
        });
        setArticles(response.articles);
        setTotalPages(Math.ceil(response.total / ITEMS_PER_PAGE));
      }
    } catch (err) {
      setError('Failed to load articles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [options.source, options.category, options.days, options.bookmarkedOnly]);

  // Reset page to 1 when filters change
  useEffect(() => {
    setPage(1);
    loadArticles(1);
  }, [options.source, options.category, options.days, options.bookmarkedOnly]);

  // Load articles when page changes (but not on initial mount or filter change)
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    loadArticles(newPage);
  }, [loadArticles]);

  const search = async (query: string) => {
    if (!query.trim()) {
      setPage(1);
      loadArticles(1);
      return;
    }
    setLoading(true);
    setError(null);
    setPage(1);
    setTotalPages(1);
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
      setPage(1);
      await loadArticles(1);
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
    page,
    totalPages,
    setPage: handlePageChange,
  };
}
