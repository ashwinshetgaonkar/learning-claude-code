import axios from 'axios';

const API_BASE = '/api';

export interface Article {
  id: number;
  source: string;
  source_id: string;
  title: string;
  authors: string[];
  abstract: string | null;
  content: string | null;
  summary: string | null;
  url: string;
  pdf_url: string | null;
  categories: string[];
  published_at: string | null;
  fetched_at: string | null;
  is_bookmarked: boolean;
}

export interface ArticlesResponse {
  articles: Article[];
  total: number;
  limit: number;
  offset: number;
}

export interface SearchResponse {
  articles: Article[];
  query: string;
  total: number;
}

export interface RefreshResponse {
  sources: Record<string, { fetched: number; status: string; error?: string }>;
  total_fetched: number;
  unique_articles: number;
  saved: number;
}

export interface Category {
  name: string;
  count: number;
}

// Articles API
export const fetchArticles = async (params: {
  source?: string;
  category?: string;
  days?: number;
  bookmarked?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ArticlesResponse> => {
  const response = await axios.get(`${API_BASE}/articles`, { params });
  return response.data;
};

export const fetchArticle = async (id: number): Promise<Article> => {
  const response = await axios.get(`${API_BASE}/articles/${id}`);
  return response.data;
};

export const searchArticles = async (query: string): Promise<SearchResponse> => {
  const response = await axios.get(`${API_BASE}/articles/search`, { params: { q: query } });
  return response.data;
};

export const summarizeArticle = async (id: number): Promise<{ summary: string; cached: boolean }> => {
  const response = await axios.post(`${API_BASE}/articles/${id}/summarize`);
  return response.data;
};

export const fetchCategories = async (): Promise<{ categories: Category[] }> => {
  const response = await axios.get(`${API_BASE}/articles/categories/list`);
  return response.data;
};

// Sources API
export const refreshAllSources = async (): Promise<RefreshResponse> => {
  const response = await axios.post(`${API_BASE}/sources/refresh`);
  return response.data;
};

export const refreshSource = async (source: string): Promise<{ fetched: number; saved: number }> => {
  const response = await axios.post(`${API_BASE}/sources/refresh/${source}`);
  return response.data;
};

// Bookmarks API
export const fetchBookmarks = async (): Promise<{ bookmarks: Article[]; total: number }> => {
  const response = await axios.get(`${API_BASE}/bookmarks`);
  return response.data;
};

export const addBookmark = async (articleId: number): Promise<{ message: string; article: Article }> => {
  const response = await axios.post(`${API_BASE}/bookmarks/${articleId}`);
  return response.data;
};

export const removeBookmark = async (articleId: number): Promise<{ message: string; article: Article }> => {
  const response = await axios.delete(`${API_BASE}/bookmarks/${articleId}`);
  return response.data;
};

// Export API
export const getArticlePdfUrl = (id: number): string => `${API_BASE}/articles/${id}/pdf`;
export const getArticleMarkdownUrl = (id: number): string => `${API_BASE}/articles/${id}/markdown`;

// Research Agents API
export interface ResearchSource {
  name: string;
  description: string;
  available: boolean;
  requires_api_key: boolean;
}

export const searchResearch = async (params: {
  q: string;
  source?: string;
}): Promise<any> => {
  const response = await axios.get(`${API_BASE}/agents/search`, { params });
  return response.data;
};

export const getResearchSources = async (): Promise<any> => {
  const response = await axios.get(`${API_BASE}/agents/sources`);
  return response.data;
};
