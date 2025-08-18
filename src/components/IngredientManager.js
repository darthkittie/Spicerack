import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Edit2, Trash2, ShoppingCart, Package } from 'lucide-react';
import { useRecipe } from '../context/RecipeContext';

const IngredientManager = () => {
  const { userIngredients, addUserIngredient, removeUserIngredient } = useRecipe();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState(null);
  const [formData, setFormData] = useState({
    ingredient_name: '',
    quantity: '1',
    unit: 'piece'
  });

  const units = [
    'piece', 'cup', 'tbsp', 'tsp', 'oz', 'lb', 'gram', 'kg', 'ml', 'liter'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.ingredient_name.trim()) return;

    try {
      await addUserIngredient(formData);
      setFormData({ ingredient_name: '', quantity: '1', unit: 'piece' });
      setShowAddForm(false);
      setEditingIngredient(null);
    } catch (error) {
      console.error('Error adding ingredient:', error);
    }
  };

  const handleEdit = (ingredient) => {
    setEditingIngredient(ingredient);
    setFormData({
      ingredient_name: ingredient.ingredient_name,
      quantity: ingredient.quantity,
      unit: ingredient.unit
    });
    setShowAddForm(true);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!formData.ingredient_name.trim()) return;

    try {
      // For now, we'll remove and re-add since we don't have an update endpoint
      await removeUserIngredient(editingIngredient.id);
      await addUserIngredient(formData);
      setFormData({ ingredient_name: '', quantity: '1', unit: 'piece' });
      setShowAddForm(false);
      setEditingIngredient(null);
    } catch (error) {
      console.error('Error updating ingredient:', error);
    }
  };

  const handleDelete = async (ingredientId) => {
    if (window.confirm('Are you sure you want to remove this ingredient?')) {
      try {
        await removeUserIngredient(ingredientId);
      } catch (error) {
        console.error('Error removing ingredient:', error);
      }
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

  const categoryIcons = {
    meat: '🥩',
    dairy: '🥛',
    produce: '🥬',
    pantry: '🫙',
    other: '📦'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-secondary-500 p-3 rounded-lg">
              <Package className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Pantry</h1>
              <p className="text-gray-600">Manage your ingredients and track what you have</p>
            </div>
          </div>
          
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>Add Ingredient</span>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-primary-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-primary-600">{userIngredients.length}</p>
            <p className="text-sm text-primary-700">Total Ingredients</p>
          </div>
          <div className="bg-secondary-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-secondary-600">
              {userIngredients.filter(ing => getIngredientCategory(ing.ingredient_name) === 'produce').length}
            </p>
            <p className="text-sm text-secondary-700">Fresh Produce</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-green-600">
              {userIngredients.filter(ing => getIngredientCategory(ing.ingredient_name) === 'pantry').length}
            </p>
            <p className="text-sm text-green-700">Pantry Items</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {userIngredients.filter(ing => getIngredientCategory(ing.ingredient_name) === 'dairy').length}
            </p>
            <p className="text-sm text-yellow-700">Dairy Items</p>
          </div>
        </div>
      </div>

      {/* Add/Edit Form Modal */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowAddForm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">
                    {editingIngredient ? 'Edit Ingredient' : 'Add New Ingredient'}
                  </h2>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingIngredient(null);
                      setFormData({ ingredient_name: '', quantity: '1', unit: 'piece' });
                    }}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="h-5 w-5 text-gray-500" />
                  </button>
                </div>

                <form onSubmit={editingIngredient ? handleUpdate : handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ingredient Name
                    </label>
                    <input
                      type="text"
                      value={formData.ingredient_name}
                      onChange={(e) => setFormData({ ...formData, ingredient_name: e.target.value })}
                      placeholder="e.g., Chicken breast, Tomatoes, Olive oil"
                      className="input-field"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Quantity
                      </label>
                      <input
                        type="text"
                        value={formData.quantity}
                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                        placeholder="1"
                        className="input-field"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Unit
                      </label>
                      <select
                        value={formData.unit}
                        onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                        className="input-field"
                      >
                        {units.map(unit => (
                          <option key={unit} value={unit}>
                            {unit.charAt(0).toUpperCase() + unit.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddForm(false);
                        setEditingIngredient(null);
                        setFormData({ ingredient_name: '', quantity: '1', unit: 'piece' });
                      }}
                      className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
                    >
                      {editingIngredient ? 'Update' : 'Add'} Ingredient
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Ingredients List */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Your Ingredients</h2>
          <p className="text-sm text-gray-600">
            {userIngredients.length === 0 
              ? 'No ingredients added yet. Start building your pantry!' 
              : `${userIngredients.length} ingredients in your pantry`
            }
          </p>
        </div>

        {userIngredients.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShoppingCart className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Empty Pantry</h3>
            <p className="text-gray-600 mb-6">
              Add ingredients to start tracking what you have and discover recipes you can make.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary"
            >
              Add Your First Ingredient
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {userIngredients.map((ingredient) => {
              const category = getIngredientCategory(ingredient.ingredient_name);
              return (
                <motion.div
                  key={ingredient.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{categoryIcons[category]}</div>
                      <div>
                        <h3 className="font-medium text-gray-900">
                          {ingredient.ingredient_name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {ingredient.quantity} {ingredient.unit}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(ingredient)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(ingredient.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default IngredientManager;
