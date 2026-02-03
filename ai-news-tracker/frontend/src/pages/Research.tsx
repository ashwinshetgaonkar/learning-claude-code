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

interface SearchResult {
  query: string;
  response?: string;
  sources?: {
    arxiv?: ArxivPaper[];
    wikipedia?: WikiArticle[];
    tavily?: TavilyResult | null;
    youtube?: YouTubeVideo[];
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
        AI-powered research assistant using Groq LLM to search arXiv, Wikipedia, and the web.
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

          {/* Individual Source Results */}
          {results.sources && (
            <div className="space-y-6">
              {/* arXiv Results */}
              {results.sources.arxiv && results.sources.arxiv.length > 0 && !results.sources.arxiv[0]?.error && (
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
              {results.sources.wikipedia && results.sources.wikipedia.length > 0 && !results.sources.wikipedia[0]?.error && (
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
              {results.sources.tavily && !results.sources.tavily.error && (
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
              {results.sources.youtube && results.sources.youtube.length > 0 && !results.sources.youtube[0]?.error && (
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
          <p className="text-sm mt-2">The AI agent will search arXiv, Wikipedia, and the web to find relevant information</p>
        </div>
      )}
    </div>
  );
}
