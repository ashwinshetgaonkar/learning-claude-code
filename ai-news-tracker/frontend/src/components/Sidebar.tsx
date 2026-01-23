import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
  categories: string[];
  onCategorySelect: (category: string) => void;
}

export function Sidebar({ categories, onCategorySelect }: SidebarProps) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'All Articles', icon: '📰' },
    { path: '/bookmarks', label: 'Bookmarks', icon: '⭐' },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-4">
        <h1 className="text-xl font-bold text-gray-900 mb-6">AI News Tracker</h1>

        <nav className="space-y-1 mb-8">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="border-t border-gray-200 pt-4">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Categories
          </h2>
          <div className="space-y-1">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => onCategorySelect(category)}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-gray-200 pt-4 mt-4">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Sources
          </h2>
          <div className="space-y-1 text-sm text-gray-600">
            <div className="flex items-center gap-2 px-3 py-1">
              <span>📄</span> arXiv Papers
            </div>
            <div className="flex items-center gap-2 px-3 py-1">
              <span>🤗</span> HuggingFace
            </div>
            <div className="flex items-center gap-2 px-3 py-1">
              <span>📰</span> AI Company Blogs
            </div>
            <div className="flex items-center gap-2 px-3 py-1">
              <span>📢</span> HN & Reddit
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
