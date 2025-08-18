import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ShoppingCart, Check, AlertCircle, ExternalLink } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';
import axios from 'axios';

const InstacartModal = ({ recipe, onClose }) => {
  const { userIngredients } = useRecipe();
  const [missingIngredients, setMissingIngredients] = useState([]);
  const [checkoutData, setCheckoutData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: ingredients, 2: checkout

  useEffect(() => {
    if (recipe && userIngredients) {
      analyzeIngredients();
    }
  }, [recipe, userIngredients]);

  const analyzeIngredients = () => {
    if (!recipe?.ingredients || !userIngredients) return;

    const userIngredientNames = userIngredients.map(ing => 
      ing.ingredient_name.toLowerCase().trim()
    );

    const missing = recipe.ingredients.filter(ingredient => {
      const ingredientLower = ingredient.toLowerCase().trim();
      return !userIngredientNames.some(userIng => 
        ingredientLower.includes(userIng) || userIng.includes(ingredientLower)
      );
    });

    setMissingIngredients(missing);
  };

  const handleInstacartCheckout = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/instacart/checkout', {
        missing_ingredients: missingIngredients
      });

      if (response.data.success) {
        setCheckoutData(response.data.checkout);
        setStep(2);
      }
    } catch (error) {
      console.error('Error with Instacart checkout:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIngredientCategory = (ingredient) => {
    const lower = ingredient.toLowerCase();
    
    if (lower.includes('chicken') || lower.includes('beef') || lower.includes('pork') || lower.includes('fish')) {
      return 'meat';
    } else if (lower.includes('milk') || lower.includes('cheese') || lower.includes('yogurt') || lower.includes('cream')) {
      return 'dairy';
    } else if (lower.includes('apple') || lower.includes('banana') || lower.includes('tomato') || lower.includes('lettuce')) {
      return 'produce';
    } else if (lower.includes('flour') || lower.includes('sugar') || lower.includes('oil') || lower.includes('salt')) {
      return 'pantry';
    } else {
      return 'other';
    }
  };

  const categoryColors = {
    meat: 'bg-red-100 text-red-800 border-red-200',
    dairy: 'bg-blue-100 text-blue-800 border-blue-200',
    produce: 'bg-green-100 text-green-800 border-green-200',
    pantry: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    other: 'bg-gray-100 text-gray-800 border-gray-200'
  };

  if (step === 1) {
    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="bg-secondary-500 p-2 rounded-lg">
                  <ShoppingCart className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Missing Ingredients</h2>
                  <p className="text-sm text-gray-600">Let's get what you need for {recipe?.title}</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Current Pantry Status */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Current Pantry</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {userIngredients.map((ingredient) => (
                    <div
                      key={ingredient.id}
                      className="p-3 bg-green-50 border border-green-200 rounded-lg"
                    >
                      <div className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-green-800">
                          {ingredient.ingredient_name}
                        </span>
                      </div>
                      <p className="text-xs text-green-600 mt-1">
                        {ingredient.quantity} {ingredient.unit}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Missing Ingredients */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Missing Ingredients ({missingIngredients.length})
                </h3>
                
                {missingIngredients.length === 0 ? (
                  <div className="text-center py-8 bg-green-50 rounded-lg">
                    <Check className="h-12 w-12 text-green-500 mx-auto mb-3" />
                    <p className="text-green-700 font-medium">You have all the ingredients!</p>
                    <p className="text-green-600 text-sm">You're ready to start cooking.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {missingIngredients.map((ingredient, index) => {
                      const category = getIngredientCategory(ingredient);
                      return (
                        <div
                          key={index}
                          className={`p-3 border rounded-lg ${categoryColors[category]}`}
                        >
                          <div className="flex items-center space-x-2">
                            <AlertCircle className="h-4 w-4" />
                            <span className="text-sm font-medium">{ingredient}</span>
                          </div>
                          <p className="text-xs mt-1 opacity-75 capitalize">
                            {category}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                {missingIngredients.length > 0 && (
                  <button
                    onClick={handleInstacartCheckout}
                    disabled={loading}
                    className="flex-1 px-4 py-3 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    {loading ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Processing...</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-2">
                        <ShoppingCart className="h-5 w-5" />
                        <span>Get from Instacart</span>
                      </div>
                    )}
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>
    );
  }

  // Step 2: Checkout
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl shadow-xl max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="bg-green-500 p-2 rounded-lg">
                <ShoppingCart className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Instacart Cart</h2>
                <p className="text-sm text-gray-600">Ready to checkout</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Checkout Content */}
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Cart Created Successfully!
              </h3>
              <p className="text-gray-600">
                Your missing ingredients have been added to your Instacart cart.
              </p>
            </div>

            {/* Cart Summary */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Items:</span>
                  <span className="font-medium">{checkoutData?.total_items || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estimated Total:</span>
                  <span className="font-medium text-green-600">
                    ${checkoutData?.estimated_total?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Delivery:</span>
                  <span className="font-medium">{checkoutData?.delivery_estimate || '2-4 hours'}</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <a
                href={checkoutData?.checkout_url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full px-4 py-3 bg-green-500 hover:bg-green-600 text-white text-center rounded-lg font-medium transition-colors"
              >
                <div className="flex items-center justify-center space-x-2">
                  <ExternalLink className="h-5 w-5" />
                  <span>Proceed to Checkout</span>
                </div>
              </a>
              
              <button
                onClick={() => setStep(1)}
                className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back to Ingredients
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default InstacartModal;
