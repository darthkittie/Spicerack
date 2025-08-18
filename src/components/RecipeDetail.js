import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Clock, Users, Star, Heart, Share2, ExternalLink, Info, ShoppingCart } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';
import InstacartModal from './InstacartModal';

const RecipeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { recipes, nutritionData, getRecipeNutrition, saveRecipe } = useRecipe();
  const [recipe, setRecipe] = useState(null);
  const [showInstacartModal, setShowInstacartModal] = useState(false);
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('');
  const [showSaveForm, setShowSaveForm] = useState(false);

  useEffect(() => {
    if (recipes.length > 0) {
      const foundRecipe = recipes.find(r => r.id === parseInt(id));
      if (foundRecipe) {
        setRecipe(foundRecipe);
        getRecipeNutrition(foundRecipe.id);
      }
    }
  }, [id, recipes, getRecipeNutrition]);

  if (!recipe) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading recipe...</p>
        </div>
      </div>
    );
  }

  const nutrition = nutritionData[recipe.id] || {};
  const hasNutrition = Object.keys(nutrition).length > 0;
  const estimatedTime = Math.max(recipe.ingredients?.length * 2, 15);
  const estimatedServings = Math.max(Math.ceil(recipe.ingredients?.length / 3), 2);

  const handleSaveRecipe = async () => {
    try {
      await saveRecipe(recipe.id, rating, notes);
      setShowSaveForm(false);
      // Show success message
      alert('Recipe saved successfully!');
    } catch (error) {
      console.error('Error saving recipe:', error);
    }
  };

  const getRatingStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <button
        key={i}
        onClick={() => setRating(i + 1)}
        className={`text-2xl transition-colors ${
          i < rating ? 'text-yellow-400' : 'text-gray-300'
        } hover:text-yellow-400`}
      >
        ★
      </button>
    ));
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
        <span>Back to Recipes</span>
      </button>

      {/* Recipe Header */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Hero Image */}
        <div className="relative h-80 bg-gradient-to-br from-primary-100 to-primary-200 overflow-hidden">
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
          <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
            <div className="text-center text-primary-600">
              <div className="text-8xl mb-4">🍽️</div>
              <p className="text-lg font-medium">Recipe Image</p>
            </div>
          </div>
          
          {/* Action Buttons Overlay */}
          <div className="absolute top-4 right-4 flex space-x-2">
            <button
              onClick={() => setShowSaveForm(true)}
              className="p-3 bg-white/90 backdrop-blur rounded-full hover:bg-white transition-colors"
            >
              <Heart className="h-5 w-5 text-red-500" />
            </button>
            <button className="p-3 bg-white/90 backdrop-blur rounded-full hover:bg-white transition-colors">
              <Share2 className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Recipe Info */}
        <div className="p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{recipe.title}</h1>
          
          {/* Quick Stats */}
          <div className="flex items-center space-x-6 mb-6">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-gray-500" />
              <span className="text-gray-700">{estimatedTime} minutes</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-gray-500" />
              <span className="text-gray-700">{estimatedServings} servings</span>
            </div>
            <div className="flex items-center space-x-2">
              <Info className="h-5 w-5 text-gray-500" />
              <span className="text-gray-700">{recipe.ingredients?.length || 0} ingredients</span>
            </div>
          </div>

          {/* Source Link */}
          {recipe.source_url && (
            <div className="mb-6">
              <a
                href={recipe.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 text-secondary-600 hover:text-secondary-700 font-medium"
              >
                <ExternalLink className="h-4 w-4" />
                <span>View Original Recipe</span>
              </a>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={() => setShowInstacartModal(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg font-medium transition-colors"
            >
              <ShoppingCart className="h-5 w-5" />
              <span>Get Ingredients</span>
            </button>
            
            <button
              onClick={() => setShowSaveForm(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              <Heart className="h-5 w-5" />
              <span>Save Recipe</span>
            </button>
          </div>
        </div>
      </div>

      {/* Recipe Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Ingredients */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Ingredients</h2>
            <div className="space-y-3">
              {recipe.ingredients?.map((ingredient, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                >
                  <span className="w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {index + 1}
                  </span>
                  <span className="text-gray-700">{ingredient}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Instructions & Nutrition */}
        <div className="lg:col-span-2 space-y-6">
          {/* Instructions */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Instructions</h2>
            <div className="space-y-4">
              {recipe.instructions?.map((instruction, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-4"
                >
                  <span className="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {index + 1}
                  </span>
                  <p className="text-gray-700 leading-relaxed">{instruction}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Nutrition Information */}
          {hasNutrition && (
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Nutrition Facts</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-secondary-50 rounded-lg">
                  <p className="text-3xl font-bold text-secondary-600">{nutrition.calories || 0}</p>
                  <p className="text-sm text-secondary-700">Calories</p>
                </div>
                <div className="text-center p-4 bg-primary-50 rounded-lg">
                  <p className="text-3xl font-bold text-primary-600">{nutrition.protein || 0}g</p>
                  <p className="text-sm text-primary-700">Protein</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-3xl font-bold text-yellow-600">{nutrition.carbs || 0}g</p>
                  <p className="text-sm text-yellow-700">Carbohydrates</p>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-3xl font-bold text-red-600">{nutrition.fat || 0}g</p>
                  <p className="text-sm text-red-700">Fat</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">{nutrition.fiber || 0}g</p>
                  <p className="text-sm text-green-700">Fiber</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-3xl font-bold text-purple-600">{nutrition.sugar || 0}g</p>
                  <p className="text-sm text-purple-700">Sugar</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Save Recipe Modal */}
      {showSaveForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Save Recipe</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Rating</label>
                <div className="flex space-x-1">
                  {getRatingStars(rating)}
                </div>
                <p className="text-sm text-gray-500 mt-1">Click stars to rate</p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add your personal notes about this recipe..."
                  className="input-field h-24 resize-none"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setShowSaveForm(false)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveRecipe}
                  className="flex-1 px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
                >
                  Save Recipe
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instacart Modal */}
      {showInstacartModal && (
        <InstacartModal
          recipe={recipe}
          onClose={() => setShowInstacartModal(false)}
        />
      )}
    </div>
  );
};

export default RecipeDetail;
