import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, Users, Info, ChevronDown, ChevronUp, ExternalLink, Heart } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';

const RecipeCard = ({ recipe }) => {
  const { nutritionData, saveRecipe } = useRecipe();
  const [showIngredients, setShowIngredients] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showNutrition, setShowNutrition] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('');
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const nutrition = nutritionData[recipe.id] || {};
  const hasNutrition = Object.keys(nutrition).length > 0;

  const estimatedTime = Math.max(recipe.ingredients?.length * 2, 15);
  const estimatedServings = Math.max(Math.ceil(recipe.ingredients?.length / 3), 2);

  const handleSave = async () => {
    try {
      await saveRecipe(recipe.id, rating, notes);
      setIsSaved(true);
      setShowSaveModal(false);
      // Reset form
      setRating(5);
      setNotes('');
    } catch (error) {
      console.error('Error saving recipe:', error);
    }
  };

  const openSaveModal = () => {
    setShowSaveModal(true);
  };

  return (
    <motion.div
      className="recipe-card recipe-card-3d max-w-md mx-auto"
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
    >
      {/* Recipe Image */}
      <div className="relative h-64 bg-gradient-to-br from-primary-100 to-primary-200 overflow-hidden">
        {recipe.image_url && !imageError ? (
          <a
            href={recipe.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full h-full hover:opacity-90 transition-opacity cursor-pointer"
            title="Click to view original recipe"
          >
            <img
              src={recipe.image_url}
              alt={recipe.title}
              className="w-full h-full object-cover"
              onError={() => setImageError(true)}
              onLoad={() => setImageLoaded(true)}
            />
          </a>
        ) : null}
        <div 
          className={`absolute inset-0 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center ${
            imageLoaded ? 'hidden' : 'flex'
          }`}
        >
          <div className="text-center text-primary-600">
            <div className="text-6xl mb-2">🍽️</div>
            <p className="text-sm font-medium">Recipe Image</p>
          </div>
        </div>
        
        {/* Recipe Info Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
          <div className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span className="text-sm">{estimatedTime} min</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4" />
                <span className="text-sm">{estimatedServings} servings</span>
              </div>
            </div>
            {recipe.source_url && (
              <a
                href={recipe.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1 hover:bg-white/20 rounded transition-colors"
                title="View original recipe"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Recipe Content */}
      <div className="p-6">
        {/* Title */}
        <div className="mb-4">
          {recipe.source_url ? (
            <a
              href={recipe.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="group block"
              title="Click to view original recipe"
            >
              <h2 className="text-2xl font-bold text-gray-900 line-clamp-2 group-hover:text-primary-600 transition-colors cursor-pointer">
                {recipe.title}
              </h2>
              <div className="flex items-center space-x-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <ExternalLink className="h-4 w-4 text-primary-500" />
                <span className="text-sm text-primary-500 font-medium">View Original Recipe</span>
              </div>
            </a>
          ) : (
            <h2 className="text-2xl font-bold text-gray-900 line-clamp-2">
              {recipe.title}
            </h2>
          )}
        </div>

        {/* Quick Stats */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-600">
                {recipe.ingredients?.length || 0}
              </p>
              <p className="text-xs text-gray-500">Ingredients</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-secondary-600">
                {recipe.instructions?.length || 0}
              </p>
              <p className="text-xs text-gray-500">Steps</p>
            </div>
          </div>
          
          {hasNutrition && (
            <button
              onClick={() => setShowNutrition(!showNutrition)}
              className="flex items-center space-x-2 px-3 py-2 bg-secondary-100 hover:bg-secondary-200 text-secondary-700 rounded-lg transition-colors"
            >
              <Info className="h-4 w-4" />
              <span className="text-sm font-medium">Nutrition</span>
              {showNutrition ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          )}
        </div>

        {/* Nutrition Information */}
        {showNutrition && hasNutrition && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6 p-4 bg-secondary-50 rounded-lg"
          >
            <h4 className="font-semibold text-secondary-800 mb-3">Nutrition Facts</h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 bg-white rounded">
                <p className="text-lg font-bold text-secondary-600">{nutrition.calories || 0}</p>
                <p className="text-xs text-gray-500">Calories</p>
              </div>
              <div className="text-center p-2 bg-white rounded">
                <p className="text-lg font-bold text-primary-600">{nutrition.protein || 0}g</p>
                <p className="text-xs text-gray-500">Protein</p>
              </div>
              <div className="text-center p-2 bg-white rounded">
                <p className="text-lg font-bold text-yellow-600">{nutrition.carbs || 0}g</p>
                <p className="text-xs text-gray-500">Carbs</p>
              </div>
              <div className="text-center p-2 bg-white rounded">
                <p className="text-lg font-bold text-red-600">{nutrition.fat || 0}g</p>
                <p className="text-xs text-gray-500">Fat</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Ingredients Section */}
        <div className="mb-6">
          <button
            onClick={() => setShowIngredients(!showIngredients)}
            className="flex items-center justify-between w-full p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span className="font-medium text-gray-900">Ingredients</span>
            {showIngredients ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {showIngredients && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 p-4 bg-gray-50 rounded-lg"
            >
              <ul className="space-y-2">
                {recipe.ingredients?.map((ingredient, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span className="text-gray-700">{ingredient}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>

        {/* Instructions Section */}
        <div className="mb-6">
          <button
            onClick={() => setShowInstructions(!showInstructions)}
            className="flex items-center justify-between w-full p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span className="font-medium text-gray-900">Instructions</span>
            {showInstructions ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {showInstructions && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 p-4 bg-gray-50 rounded-lg"
            >
              <ol className="space-y-3">
                {recipe.instructions?.map((instruction, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <span className="w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{instruction}</span>
                  </li>
                ))}
              </ol>
            </motion.div>
          )}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-6">
          <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
            {estimatedTime} min
          </span>
          <span className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium">
            {estimatedServings} servings
          </span>
          {recipe.ingredients?.length > 0 && (
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              {recipe.ingredients.length} ingredients
            </span>
          )}
        </div>

        {/* Save Button */}
        <div className="flex justify-center mb-4">
          <button
            onClick={openSaveModal}
            disabled={isSaved}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
              isSaved
                ? 'bg-green-100 text-green-700 cursor-not-allowed'
                : 'bg-primary-500 hover:bg-primary-600 text-white hover:scale-105'
            }`}
          >
            <Heart className={`h-5 w-5 ${isSaved ? 'fill-current' : ''}`} />
            <span>{isSaved ? 'Recipe Saved!' : 'Save Recipe'}</span>
          </button>
        </div>

        {/* View Original Recipe Button */}
        {recipe.source_url && (
          <div className="flex justify-center">
            <a
              href={recipe.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-all hover:scale-105"
              title="Visit the original recipe website"
            >
              <ExternalLink className="h-5 w-5" />
              <span>View Original Recipe</span>
            </a>
          </div>
        )}
      </div>

      {/* Save Recipe Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Save Recipe</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rating
                </label>
                <div className="flex space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      className={`p-2 rounded-lg transition-colors ${
                        rating >= star
                          ? 'bg-yellow-100 text-yellow-600'
                          : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                      }`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add your personal notes about this recipe..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows="3"
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  Save Recipe
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default RecipeCard;
