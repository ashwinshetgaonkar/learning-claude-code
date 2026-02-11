import { useState, useEffect } from 'react';
import { searchResearch, getResearchSources } from '../api/client';

interface ArxivPaper {
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  pdf_url: string;
  published: string;
  error?: string;
}

interface WikiArticle {
  title: string;
  summary: string;
  url: string;
  error?: string;
}

interface TavilyResult {
  answer?: string;
  results?: Array<{
    title: string;
    content: string;
    url: string;
  }>;
  error?: string;
}

interface YouTubeVideo {
  title: string;
  channel: string;
  description: string;
  url: string;
  thumbnail_url: string;
  published_at: string;
  error?: string;
}

interface SemanticScholarPaper {
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  year: number | null;
  citation_count: number;
  error?: string;
}

interface HuggingFaceModel {
  model_id: string;
  author: string;
  downloads: number;
  likes: number;
  tags: string[];
  url: string;
  error?: string;
}

interface GitHubRepo {
  name: string;
  full_name: string;
  description: string;
  url: string;
  stars: number;
  language: string | null;
  topics: string[];
  error?: string;
}

interface PapersWithCodeResult {
  title: string;
  abstract: string;
  url: string;
  repository_url?: string | null;
  error?: string;
}

interface AnthropicArticle {
  title: string;
  description: string;
  url: string;
  error?: string;
}

interface SearchResult {
  query: string;
  response?: string;
  sources?: {
    arxiv?: ArxivPaper[];
    wikipedia?: WikiArticle[];
    tavily?: TavilyResult | null;
    youtube?: YouTubeVideo[];
    semantic_scholar?: SemanticScholarPaper[];
    huggingface?: HuggingFaceModel[];
    github?: GitHubRepo[];
    papers_with_code?: PapersWithCodeResult[];
    anthropic?: AnthropicArticle[];
  };
  success: boolean;
}

interface ResearchSource {
  name: string;
  description: string;
  available: boolean;
  requires_api_key: boolean;
}

interface SourcesResponse {
  sources: ResearchSource[];
  llm?: {
    provider: string;
    model: string;
    configured: boolean;
  };
}

export default function Research() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [sourcesInfo, setSourcesInfo] = useState<SourcesResponse | null>(null);
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeResultTab, setActiveResultTab] = useState<string>('all');

  // Load available sources on mount
  useEffect(() => {
    const loadSources = async () => {
      try {
        const data = await getResearchSources();
        setSourcesInfo(data as SourcesResponse);
      } catch (err) {
        console.error('Failed to load sources:', err);
      }
    };
    loadSources();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setActiveResultTab('all');

    try {
      const params: { q: string; source?: string } = { q: query };
      if (selectedSource) {
        params.source = selectedSource;
      }
      const data = await searchResearch(params as any);
      setResults(data as SearchResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="flex-1 p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Research Agent</h1>
      <p className="text-gray-600 mb-6">
        AI-powered research assistant using Groq LLM to search arXiv, Semantic Scholar, Wikipedia, HuggingFace, GitHub, and more.
      </p>

      {/* LLM Status */}
      {sourcesInfo?.llm && (
        <div className={`mb-4 text-sm ${sourcesInfo.llm.configured ? 'text-green-600' : 'text-red-600'}`}>
          LLM: {sourcesInfo.llm.provider} / {sourcesInfo.llm.model} -
          {sourcesInfo.llm.configured ? ' Connected' : ' Not configured (add GROQ_API_KEY)'}
        </div>
      )}

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about any topic (e.g., transformer architecture, quantum computing)..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Searching...
              </>
            ) : (
              'Search'
            )}
          </button>
        </div>

        {/* Source Selection */}
        <div className="flex gap-4 items-center flex-wrap">
          <span className="text-sm text-gray-600">Source:</span>
          <label
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm cursor-pointer transition-colors ${
              selectedSource === '' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            <input
              type="radio"
              name="source"
              value=""
              checked={selectedSource === ''}
              onChange={() => setSelectedSource('')}
              className="sr-only"
            />
            AI Agent (All)
          </label>
          {sourcesInfo?.sources.map((source) => (
            <label
              key={source.name}
              className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm cursor-pointer transition-colors ${
                selectedSource === source.name
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600'
              } ${!source.available ? 'opacity-50' : ''}`}
            >
              <input
                type="radio"
                name="source"
                value={source.name}
                checked={selectedSource === source.name}
                onChange={() => setSelectedSource(source.name)}
                disabled={!source.available}
                className="sr-only"
              />
              {source.name}
              {!source.available && ' (unavailable)'}
            </label>
          ))}
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">
            Results for "{results.query}"
          </h2>

          {/* Agent Response */}
          {results.response && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
                <span className="text-lg">🤖</span> AI Research Summary
              </h3>
              <div className="text-gray-700 whitespace-pre-wrap">{results.response}</div>
            </div>
          )}

          {/* Source Navigation Tabs */}
          {results.sources && (
            <div>
              {/* Tab Navigation */}
              <div className="flex gap-2 mb-4 flex-wrap border-b border-gray-200 pb-3">
                <button
                  onClick={() => setActiveResultTab('all')}
                  className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                    activeResultTab === 'all'
                      ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-600'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  All Sources
                </button>
                {results.sources.arxiv && results.sources.arxiv.length > 0 && !results.sources.arxiv[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('arxiv')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'arxiv'
                        ? 'bg-orange-100 text-orange-700 border-b-2 border-orange-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    arXiv ({results.sources.arxiv.length})
                  </button>
                )}
                {results.sources.wikipedia && results.sources.wikipedia.length > 0 && !results.sources.wikipedia[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('wikipedia')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'wikipedia'
                        ? 'bg-gray-300 text-gray-800 border-b-2 border-gray-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Wikipedia ({results.sources.wikipedia.length})
                  </button>
                )}
                {results.sources.tavily && !results.sources.tavily.error && (
                  <button
                    onClick={() => setActiveResultTab('tavily')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'tavily'
                        ? 'bg-green-100 text-green-700 border-b-2 border-green-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Tavily ({results.sources.tavily.results?.length || 0})
                  </button>
                )}
                {results.sources.youtube && results.sources.youtube.length > 0 && !results.sources.youtube[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('youtube')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'youtube'
                        ? 'bg-red-100 text-red-700 border-b-2 border-red-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    YouTube ({results.sources.youtube.length})
                  </button>
                )}
                {results.sources.semantic_scholar && results.sources.semantic_scholar.length > 0 && !results.sources.semantic_scholar[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('semantic_scholar')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'semantic_scholar'
                        ? 'bg-purple-100 text-purple-700 border-b-2 border-purple-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Semantic Scholar ({results.sources.semantic_scholar.length})
                  </button>
                )}
                {results.sources.huggingface && results.sources.huggingface.length > 0 && !results.sources.huggingface[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('huggingface')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'huggingface'
                        ? 'bg-yellow-100 text-yellow-700 border-b-2 border-yellow-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    HuggingFace ({results.sources.huggingface.length})
                  </button>
                )}
                {results.sources.github && results.sources.github.length > 0 && !results.sources.github[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('github')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'github'
                        ? 'bg-slate-200 text-slate-700 border-b-2 border-slate-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    GitHub ({results.sources.github.length})
                  </button>
                )}
                {results.sources.papers_with_code && results.sources.papers_with_code.length > 0 && !results.sources.papers_with_code[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('papers_with_code')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'papers_with_code'
                        ? 'bg-teal-100 text-teal-700 border-b-2 border-teal-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Papers With Code ({results.sources.papers_with_code.length})
                  </button>
                )}
                {results.sources.anthropic && results.sources.anthropic.length > 0 && !results.sources.anthropic[0]?.error && (
                  <button
                    onClick={() => setActiveResultTab('anthropic')}
                    className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                      activeResultTab === 'anthropic'
                        ? 'bg-amber-100 text-amber-700 border-b-2 border-amber-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Anthropic ({results.sources.anthropic.length})
                  </button>
                )}
              </div>

              {/* Tab Content */}
              <div className="space-y-6">
                {/* arXiv Results */}
                {(activeResultTab === 'all' || activeResultTab === 'arxiv') &&
                 results.sources.arxiv && results.sources.arxiv.length > 0 && !results.sources.arxiv[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-sm">arXiv</span>
                      Academic Papers
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.arxiv.map((paper, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                              {paper.title}
                            </a>
                            <p className="text-sm text-gray-500 mt-1">{paper.authors?.join(', ')}</p>
                            <p className="text-sm text-gray-700 mt-2">{paper.abstract}</p>
                            {paper.pdf_url && (
                              <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="text-xs text-red-600 hover:underline mt-2 inline-block">
                                PDF
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Wikipedia Results */}
                {(activeResultTab === 'all' || activeResultTab === 'wikipedia') &&
                 results.sources.wikipedia && results.sources.wikipedia.length > 0 && !results.sources.wikipedia[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm">Wikipedia</span>
                      Articles
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.wikipedia.map((article, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                              {article.title}
                            </a>
                            <p className="text-sm text-gray-700 mt-2">{article.summary}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Tavily Results */}
                {(activeResultTab === 'all' || activeResultTab === 'tavily') &&
                 results.sources.tavily && !results.sources.tavily.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">Tavily</span>
                      Web Results
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg space-y-4">
                      {results.sources.tavily.answer && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded">
                          <p className="text-sm font-medium text-green-800 mb-1">AI Answer:</p>
                          <p className="text-sm text-gray-700">{results.sources.tavily.answer}</p>
                        </div>
                      )}
                      {results.sources.tavily.results && results.sources.tavily.results.length > 0 && (
                        <div className="space-y-3">
                          {results.sources.tavily.results.map((result, idx) => (
                            <div key={idx} className="p-3 bg-white rounded border">
                              <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                                {result.title}
                              </a>
                              <p className="text-sm text-gray-700 mt-2">{result.content}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* YouTube Results */}
                {(activeResultTab === 'all' || activeResultTab === 'youtube') &&
                 results.sources.youtube && results.sources.youtube.length > 0 && !results.sources.youtube[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm">YouTube</span>
                      Videos
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.youtube.map((video, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border flex gap-4">
                            <img
                              src={video.thumbnail_url}
                              alt={video.title}
                              className="w-32 h-20 rounded object-cover flex-shrink-0"
                            />
                            <div className="flex-1 min-w-0">
                              <a href={video.url} target="_blank" rel="noopener noreferrer"
                                 className="text-blue-600 hover:underline font-medium line-clamp-2">
                                {video.title}
                              </a>
                              <p className="text-sm text-gray-500 mt-1">{video.channel}</p>
                              <p className="text-sm text-gray-700 mt-1 line-clamp-2">{video.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Semantic Scholar Results */}
                {(activeResultTab === 'all' || activeResultTab === 'semantic_scholar') &&
                 results.sources.semantic_scholar && results.sources.semantic_scholar.length > 0 && !results.sources.semantic_scholar[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm">Semantic Scholar</span>
                      Papers
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.semantic_scholar.map((paper, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                              {paper.title}
                            </a>
                            <div className="flex gap-3 text-sm text-gray-500 mt-1">
                              {paper.authors?.length > 0 && <span>{paper.authors.join(', ')}</span>}
                              {paper.year && <span>({paper.year})</span>}
                              <span>{paper.citation_count} citations</span>
                            </div>
                            {paper.abstract && <p className="text-sm text-gray-700 mt-2">{paper.abstract}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* HuggingFace Results */}
                {(activeResultTab === 'all' || activeResultTab === 'huggingface') &&
                 results.sources.huggingface && results.sources.huggingface.length > 0 && !results.sources.huggingface[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-sm">HuggingFace</span>
                      Models
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.huggingface.map((model, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={model.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium font-mono text-sm">
                              {model.model_id}
                            </a>
                            <div className="flex gap-4 text-sm text-gray-500 mt-1">
                              <span>{model.downloads.toLocaleString()} downloads</span>
                              <span>{model.likes} likes</span>
                            </div>
                            {model.tags.length > 0 && (
                              <div className="flex gap-1 flex-wrap mt-2">
                                {model.tags.map((tag, i) => (
                                  <span key={i} className="px-2 py-0.5 bg-yellow-50 text-yellow-700 rounded text-xs">{tag}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* GitHub Results */}
                {(activeResultTab === 'all' || activeResultTab === 'github') &&
                 results.sources.github && results.sources.github.length > 0 && !results.sources.github[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-slate-200 text-slate-700 rounded text-sm">GitHub</span>
                      Repositories
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.github.map((repo, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={repo.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium font-mono text-sm">
                              {repo.full_name}
                            </a>
                            <div className="flex gap-3 text-sm text-gray-500 mt-1">
                              <span>{repo.stars.toLocaleString()} stars</span>
                              {repo.language && <span>{repo.language}</span>}
                            </div>
                            {repo.description && <p className="text-sm text-gray-700 mt-2">{repo.description}</p>}
                            {repo.topics.length > 0 && (
                              <div className="flex gap-1 flex-wrap mt-2">
                                {repo.topics.map((topic, i) => (
                                  <span key={i} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-xs">{topic}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Papers With Code Results */}
                {(activeResultTab === 'all' || activeResultTab === 'papers_with_code') &&
                 results.sources.papers_with_code && results.sources.papers_with_code.length > 0 && !results.sources.papers_with_code[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-teal-100 text-teal-700 rounded text-sm">Papers With Code</span>
                      Papers & Implementations
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.papers_with_code.map((paper, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                              {paper.title}
                            </a>
                            {paper.abstract && <p className="text-sm text-gray-700 mt-2">{paper.abstract}</p>}
                            {paper.repository_url && (
                              <a href={paper.repository_url} target="_blank" rel="noopener noreferrer" className="text-xs text-teal-600 hover:underline mt-2 inline-block">
                                View Code
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Anthropic Results */}
                {(activeResultTab === 'all' || activeResultTab === 'anthropic') &&
                 results.sources.anthropic && results.sources.anthropic.length > 0 && !results.sources.anthropic[0]?.error && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-sm">Anthropic</span>
                      Research Articles
                    </h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="space-y-4">
                        {results.sources.anthropic.map((article, idx) => (
                          <div key={idx} className="p-3 bg-white rounded border">
                            <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                              {article.title}
                            </a>
                            {article.description && <p className="text-sm text-gray-700 mt-2">{article.description}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!results && !loading && !error && (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p className="mt-4">Enter a research query to search across multiple sources</p>
          <p className="text-sm mt-2">The AI agent will search arXiv, Semantic Scholar, Wikipedia, HuggingFace, GitHub, and more</p>
        </div>
      )}
    </div>
  );
}
