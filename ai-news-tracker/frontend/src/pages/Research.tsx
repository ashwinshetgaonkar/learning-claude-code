import { useState, useCallback } from 'react';
import {
  searchResearch,
  getResearchSources,
  ResearchSearchResponse,
  ResearchSource,
} from '../api/client';

export default function Research() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ResearchSearchResponse | null>(null);
  const [sources, setSources] = useState<ResearchSource[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>(['arxiv', 'wikipedia', 'tavily']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sourcesLoaded, setSourcesLoaded] = useState(false);

  // Load available sources on first render
  const loadSources = useCallback(async () => {
    if (sourcesLoaded) return;
    try {
      const data = await getResearchSources();
      setSources(data.sources);
      setSourcesLoaded(true);
    } catch (err) {
      console.error('Failed to load sources:', err);
    }
  }, [sourcesLoaded]);

  // Load sources on mount
  useState(() => {
    loadSources();
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchResearch({
        q: query,
        sources: selectedSources.join(','),
        max_results: 5,
      });
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (source: string) => {
    setSelectedSources((prev) =>
      prev.includes(source)
        ? prev.filter((s) => s !== source)
        : [...prev, source]
    );
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Research Agent</h1>
      <p className="text-gray-600 mb-6">
        Search across multiple sources including arXiv papers, Wikipedia, and web results.
      </p>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a topic (e.g., transformer architecture, LLM training)..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !query.trim() || selectedSources.length === 0}
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
        <div className="flex gap-4 items-center">
          <span className="text-sm text-gray-600">Sources:</span>
          {sources.map((source) => (
            <label
              key={source.name}
              className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm cursor-pointer transition-colors ${
                selectedSources.includes(source.name)
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600'
              } ${!source.available ? 'opacity-50' : ''}`}
            >
              <input
                type="checkbox"
                checked={selectedSources.includes(source.name)}
                onChange={() => toggleSource(source.name)}
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
        <div className="space-y-8">
          <h2 className="text-lg font-semibold">
            Results for "{results.query}"
          </h2>

          {/* Tavily Answer */}
          {results.sources.tavily?.answer && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">AI Summary</h3>
              <p className="text-gray-700">{results.sources.tavily.answer}</p>
            </div>
          )}

          {/* arXiv Results */}
          {results.sources.arxiv && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-sm">arXiv</span>
                Academic Papers ({results.sources.arxiv.count})
              </h3>
              {results.sources.arxiv.error ? (
                <p className="text-red-600">{results.sources.arxiv.error}</p>
              ) : results.sources.arxiv.results.length === 0 ? (
                <p className="text-gray-500">No papers found</p>
              ) : (
                <div className="space-y-4">
                  {results.sources.arxiv.results.map((paper, idx) => (
                    <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <a
                        href={paper.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {paper.title}
                      </a>
                      <p className="text-sm text-gray-500 mt-1">
                        {paper.authors.slice(0, 3).join(', ')}
                        {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
                      </p>
                      <p className="text-gray-700 mt-2 text-sm line-clamp-3">{paper.abstract}</p>
                      <div className="flex gap-2 mt-2">
                        {paper.pdf_url && (
                          <a
                            href={paper.pdf_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-red-600 hover:underline"
                          >
                            PDF
                          </a>
                        )}
                        {paper.categories.slice(0, 3).map((cat) => (
                          <span key={cat} className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                            {cat}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Wikipedia Results */}
          {results.sources.wikipedia && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm">Wikipedia</span>
                Articles ({results.sources.wikipedia.count})
              </h3>
              {results.sources.wikipedia.error ? (
                <p className="text-red-600">{results.sources.wikipedia.error}</p>
              ) : results.sources.wikipedia.results.length === 0 ? (
                <p className="text-gray-500">No articles found</p>
              ) : (
                <div className="space-y-4">
                  {results.sources.wikipedia.results.map((article, idx) => (
                    <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {article.title}
                      </a>
                      <p className="text-gray-700 mt-2 text-sm">{article.summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tavily Web Results */}
          {results.sources.tavily && results.sources.tavily.results && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">Tavily</span>
                Web Results ({results.sources.tavily.results.length})
              </h3>
              {results.sources.tavily.error ? (
                <p className="text-red-600">{results.sources.tavily.error}</p>
              ) : results.sources.tavily.results.length === 0 ? (
                <p className="text-gray-500">No web results found</p>
              ) : (
                <div className="space-y-4">
                  {results.sources.tavily.results.map((result, idx) => (
                    <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {result.title}
                      </a>
                      <p className="text-gray-700 mt-2 text-sm line-clamp-3">{result.content}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        Relevance: {(result.score * 100).toFixed(0)}%
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p className="mt-4">Enter a search query to find research from multiple sources</p>
        </div>
      )}
    </div>
  );
}
