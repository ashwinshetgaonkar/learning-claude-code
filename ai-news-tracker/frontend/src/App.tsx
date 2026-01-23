import { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Home } from './pages/Home';
import { Bookmarks } from './pages/Bookmarks';
import { ArticleDetail } from './pages/ArticleDetail';
import { Article } from './api/client';

const CATEGORIES = [
  'AI',
  'Machine Learning',
  'Generative AI',
  'Tech News',
  'Research',
  'Discussion',
  'Project',
];

function App() {
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('');

  const handleViewDetail = useCallback((article: Article) => {
    setSelectedArticle(article);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedArticle(null);
  }, []);

  const handleUpdateArticle = useCallback((updated: Article) => {
    setSelectedArticle(updated);
  }, []);

  const handleCategorySelect = useCallback((category: string) => {
    setSelectedCategory(category === selectedCategory ? '' : category);
  }, [selectedCategory]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar categories={CATEGORIES} onCategorySelect={handleCategorySelect} />

      <Routes>
        <Route path="/" element={
          <Home
            onViewDetail={handleViewDetail}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
          />
        } />
        <Route path="/bookmarks" element={<Bookmarks onViewDetail={handleViewDetail} />} />
      </Routes>

      {selectedArticle && (
        <ArticleDetail
          article={selectedArticle}
          onClose={handleCloseDetail}
          onUpdate={handleUpdateArticle}
        />
      )}
    </div>
  );
}

export default App;
