interface FilterBarProps {
  sources: string[];
  categories: string[];
  selectedSource: string;
  selectedCategory: string;
  selectedDays: number | null;
  onSourceChange: (source: string) => void;
  onCategoryChange: (category: string) => void;
  onDaysChange: (days: number | null) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

const SOURCE_LABELS: Record<string, string> = {
  arxiv: 'arXiv',
  huggingface: 'HuggingFace',
  blog: 'AI Blogs',
  aggregator: 'News',
};

const DAY_OPTIONS = [
  { value: null, label: 'All Time' },
  { value: 1, label: 'Today' },
  { value: 7, label: 'This Week' },
  { value: 30, label: 'This Month' },
];

export function FilterBar({
  sources,
  categories,
  selectedSource,
  selectedCategory,
  selectedDays,
  onSourceChange,
  onCategoryChange,
  onDaysChange,
  onRefresh,
  isLoading,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 py-3 px-4 bg-white border-b border-gray-200">
      <span className="text-sm font-medium text-gray-600">Filters:</span>

      <select
        value={selectedSource}
        onChange={(e) => onSourceChange(e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Sources</option>
        {sources.map((source) => (
          <option key={source} value={source}>
            {SOURCE_LABELS[source] || source}
          </option>
        ))}
      </select>

      <select
        value={selectedCategory}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Categories</option>
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>

      <select
        value={selectedDays === null ? '' : selectedDays.toString()}
        onChange={(e) => onDaysChange(e.target.value ? parseInt(e.target.value) : null)}
        className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {DAY_OPTIONS.map((option) => (
          <option key={option.label} value={option.value === null ? '' : option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="ml-auto px-4 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <svg
            className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      )}
    </div>
  );
}
