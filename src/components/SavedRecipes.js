import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Trash2, Star, Clock, Users, ExternalLink, Search } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';

const SavedRecipes = () => {
  const { savedRecipes } = useRecipe();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRating, setFilterRating] = useState('all');

  const filteredRecipes = savedRecipes.filter(recipe => {
    const matchesSearch = recipe.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRating = filterRating === 'all' || recipe.rating >= parseInt(filterRating);
    return matchesSearch && matchesRating;
  });

  const getRatingStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const handleDeleteRecipe = (recipeId) => {
    if (window.confirm('Are you sure you want to remove this recipe from your saved list?')) {
      // This would call a delete function from the context
      console.log('Delete recipe:', recipeId);
    }
  };

  if (savedRecipes.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md mx-auto">
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Heart className="h-12 w-12 text-red-500" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Saved Recipes Yet
          </h3>
          <p className="text-gray-600 mb-6">
            Start swiping through recipes and save the ones you love! Your saved recipes will appear here.
          </p>
          <div className="text-sm text-gray-500">
            <p>💡 Tip: Swipe right on recipes you like to save them</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-red-500 p-3 rounded-lg">
              <Heart className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Saved Recipes</h1>
              <p className="text-gray-600">Your collection of favorite recipes</p>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-2xl font-bold text-red-600">{savedRecipes.length}</p>
            <p className="text-sm text-gray-600">Total Saved</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-red-600">
              {savedRecipes.filter(r => r.rating === 5).length}
            </p>
            <p className="text-sm text-red-700">5-Star Recipes</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {savedRecipes.filter(r => r.rating >= 4).length}
            </p>
            <p className="text-sm text-yellow-700">4+ Star Recipes</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-green-600">
              {savedRecipes.filter(r => r.notes && r.notes.trim()).length}
            </p>
            <p className="text-sm text-green-700">With Notes</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-blue-600">
              {Math.round(savedRecipes.reduce((acc, r) => acc + r.rating, 0) / savedRecipes.length * 10) / 10}
            </p>
            <p className="text-sm text-blue-700">Avg Rating</p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search saved recipes..."
              className="input-field pl-10"
            />
          </div>
          
          <select
            value={filterRating}
            onChange={(e) => setFilterRating(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
          >
            <option value="all">All Ratings</option>
            <option value="5">5 Stars</option>
            <option value="4">4+ Stars</option>
            <option value="3">3+ Stars</option>
          </select>
        </div>
        
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredRecipes.length} of {savedRecipes.length} saved recipes
        </div>
      </div>

      {/* Recipes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredRecipes.map((recipe, index) => (
            <motion.div
              key={recipe.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Recipe Image */}
              <div className="relative h-48 bg-gradient-to-br from-red-100 to-red-200 overflow-hidden">
                {recipe.image_url ? (
                  <img
                    src={recipe.image_url}
                    alt={recipe.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="absolute inset-0 bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center">
                  <div className="text-center text-red-600">
                    <div className="text-4xl mb-2">🍽️</div>
                    <p className="text-sm font-medium">Recipe Image</p>
                  </div>
                </div>
                
                {/* Rating Badge */}
                <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-2 py-1 rounded-full">
                  <div className="flex items-center space-x-1">
                    {getRatingStars(recipe.rating)}
                  </div>
                </div>
              </div>

              {/* Recipe Content */}
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2">
                  {recipe.title}
                </h3>

                {/* Quick Stats */}
                <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>{Math.max(recipe.ingredients?.length * 2, 15)} min</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Users className="h-4 w-4" />
                    <span>{Math.max(Math.ceil(recipe.ingredients?.length / 3), 2)} servings</span>
                  </div>
                </div>

                {/* Notes */}
                {recipe.notes && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <span className="font-medium">Notes:</span> {recipe.notes}
                    </p>
                  </div>
                )}

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                    {recipe.ingredients?.length || 0} ingredients
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                    {recipe.instructions?.length || 0} steps
                  </span>
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    {recipe.rating} stars
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  {recipe.source_url && (
                    <a
                      href={recipe.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                      <span>View Recipe</span>
                    </a>
                  )}
                  
                  <button
                    onClick={() => handleDeleteRecipe(recipe.id)}
                    className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State for Filtered Results */}
      {filteredRecipes.length === 0 && savedRecipes.length > 0 && (
        <div className="text-center py-12">
          <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md mx-auto">
            <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Recipes Found</h3>
            <p className="text-gray-600 mb-4">
              No saved recipes match your current search or filter criteria.
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterRating('all');
              }}
              className="btn-primary"
            >
              Clear Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedRecipes;
