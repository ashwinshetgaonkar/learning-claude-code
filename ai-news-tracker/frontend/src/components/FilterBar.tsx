interface FilterBarProps {
  sources: string[];
  categories: string[];
  selectedSource: string;
  selectedCategory: string;
  selectedDays: number | null;
  onSourceChange: (source: string) => void;
  onCategoryChange: (category: string) => void;
  onDaysChange: (days: number | null) => void;
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
    </div>
  );
}
