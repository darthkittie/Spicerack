import React, { useState, useEffect } from 'react';
import { useSwipeable } from 'react-swipeable';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Heart, X, ArrowLeft, ArrowRight, Info, ShoppingCart } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';
import RecipeCard from './RecipeCard';
import InstacartModal from './InstacartModal';

const RecipeSwiper = () => {
  const {
    recipes,
    currentRecipeIndex,
    loading,
    error,
    searchQuery,
    scrapeRecipes,
    swipeLeft,
    swipeRight,
    nextRecipe,
    previousRecipe,
    getRecipeNutrition,
  } = useRecipe();

  const [searchInput, setSearchInput] = useState('');
  const [showInstacartModal, setShowInstacartModal] = useState(false);
  const [currentRecipe, setCurrentRecipe] = useState(null);

  useEffect(() => {
    if (recipes.length > 0 && currentRecipeIndex < recipes.length) {
      setCurrentRecipe(recipes[currentRecipeIndex]);
      // Get nutrition data for the current recipe
      getRecipeNutrition(recipes[currentRecipeIndex].id);
    }
  }, [recipes, currentRecipeIndex, getRecipeNutrition]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      scrapeRecipes(searchInput.trim(), 10);
    }
  };

  const handleSwipeLeft = () => {
    swipeLeft();
  };

  const handleSwipeRight = () => {
    swipeRight();
  };

  const swipeHandlers = useSwipeable({
    onSwipedLeft: handleSwipeLeft,
    onSwipedRight: handleSwipeRight,
    preventDefaultTouchmoveEvent: true,
    trackMouse: true,
  });

  const handleInstacartCheckout = () => {
    if (currentRecipe) {
      setShowInstacartModal(true);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Scraping delicious recipes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="bg-red-100 p-4 rounded-lg mb-4">
            <p className="text-red-600">Error: {error}</p>
          </div>
          <button
            onClick={() => scrapeRecipes('chicken recipes')}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (recipes.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md mx-auto">
          <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Discover New Recipes
          </h3>
          <p className="text-gray-600 mb-6">
            Search for your favorite dishes and start swiping through delicious recipes!
          </p>
          
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search for recipes..."
                className="input-field pl-10"
              />
            </div>
            <button type="submit" className="btn-primary w-full">
              Find Recipes
            </button>
          </form>
          
          <div className="mt-6">
            <p className="text-sm text-gray-500 mb-3">Popular searches:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {['chicken recipes', 'pasta dishes', 'vegetarian meals', 'quick dinner'].map((term) => (
                <button
                  key={term}
                  onClick={() => {
                    setSearchInput(term);
                    scrapeRecipes(term);
                  }}
                  className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-sm transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <form onSubmit={handleSearch} className="flex space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search for recipes..."
              className="input-field pl-10"
            />
          </div>
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
        
        {searchQuery && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing results for: <span className="font-medium text-gray-900">{searchQuery}</span>
            </p>
            <p className="text-sm text-gray-500">
              {currentRecipeIndex + 1} of {recipes.length} recipes
            </p>
          </div>
        )}
      </div>

      {/* Recipe Swiper */}
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="relative w-full max-w-md">
          {/* Navigation Arrows */}
          <button
            onClick={previousRecipe}
            disabled={currentRecipeIndex === 0}
            className={`absolute left-4 top-1/2 transform -translate-y-1/2 z-10 p-2 rounded-full shadow-lg transition-all ${
              currentRecipeIndex === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-white text-gray-700 hover:bg-gray-50 hover:scale-110'
            }`}
          >
            <ArrowLeft className="h-6 w-6" />
          </button>

          <button
            onClick={nextRecipe}
            disabled={currentRecipeIndex >= recipes.length - 1}
            className={`absolute right-4 top-1/2 transform -translate-y-1/2 z-10 p-2 rounded-full shadow-lg transition-all ${
              currentRecipeIndex >= recipes.length - 1
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-white text-gray-700 hover:bg-gray-50 hover:scale-110'
            }`}
          >
            <ArrowRight className="h-6 w-6" />
          </button>

          {/* Recipe Card */}
          <AnimatePresence mode="wait">
            {currentRecipe && (
              <motion.div
                key={currentRecipe.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3 }}
                className="w-full"
                {...swipeHandlers}
              >
                <RecipeCard recipe={currentRecipe} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Swipe Instructions */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500 mb-2">Swipe or use arrows to navigate</p>
            <div className="flex items-center justify-center space-x-4">
              <div className="flex items-center space-x-2">
                <X className="h-5 w-5 text-red-500" />
                <span className="text-sm text-gray-600">Swipe left to skip</span>
              </div>
              <div className="flex items-center space-x-2">
                <Heart className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-600">Swipe right to save</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {currentRecipe && (
        <div className="flex justify-center space-x-4">
          <button
            onClick={handleSwipeLeft}
            className="flex items-center space-x-2 px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
          >
            <X className="h-5 w-5" />
            <span>Skip</span>
          </button>
          
          <button
            onClick={handleInstacartCheckout}
            className="flex items-center space-x-2 px-6 py-3 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg font-medium transition-colors"
          >
            <ShoppingCart className="h-5 w-5" />
            <span>Get Ingredients</span>
          </button>
          
          <button
            onClick={handleSwipeRight}
            className="flex items-center space-x-2 px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
          >
            <Heart className="h-5 w-5" />
            <span>Save</span>
          </button>
        </div>
      )}

      {/* Instacart Modal */}
      {showInstacartModal && (
        <InstacartModal
          recipe={currentRecipe}
          onClose={() => setShowInstacartModal(false)}
        />
      )}
    </div>
  );
};

export default RecipeSwiper;
