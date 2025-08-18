import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const RecipeContext = createContext();

const initialState = {
  recipes: [],
  currentRecipeIndex: 0,
  userIngredients: [],
  savedRecipes: [],
  loading: false,
  error: null,
  searchQuery: '',
  nutritionData: {},
};

const recipeReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_RECIPES':
      return { ...state, recipes: action.payload, currentRecipeIndex: 0, loading: false };
    
    case 'NEXT_RECIPE':
      return { 
        ...state, 
        currentRecipeIndex: Math.min(state.currentRecipeIndex + 1, state.recipes.length - 1) 
      };
    
    case 'PREVIOUS_RECIPE':
      return { 
        ...state, 
        currentRecipeIndex: Math.max(state.currentRecipeIndex - 1, 0) 
      };
    
    case 'SWIPE_LEFT':
      return { ...state, currentRecipeIndex: state.currentRecipeIndex + 1 };
    
    case 'SWIPE_RIGHT':
      return { ...state, currentRecipeIndex: state.currentRecipeIndex + 1 };
    
    case 'SET_USER_INGREDIENTS':
      return { ...state, userIngredients: action.payload };
    
    case 'ADD_USER_INGREDIENT':
      return { 
        ...state, 
        userIngredients: [...state.userIngredients, action.payload] 
      };
    
    case 'REMOVE_USER_INGREDIENT':
      return { 
        ...state, 
        userIngredients: state.userIngredients.filter(ing => ing.id !== action.payload) 
      };
    
    case 'SET_SAVED_RECIPES':
      return { ...state, savedRecipes: action.payload };
    
    case 'SAVE_RECIPE':
      return { 
        ...state, 
        savedRecipes: [...state.savedRecipes, action.payload] 
      };
    
    case 'SET_SEARCH_QUERY':
      return { ...state, searchQuery: action.payload };
    
    case 'SET_NUTRITION_DATA':
      return { 
        ...state, 
        nutritionData: { ...state.nutritionData, ...action.payload } 
      };
    
    default:
      return state;
  }
};

export const RecipeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(recipeReducer, initialState);

  // API functions
  const scrapeRecipes = async (query, maxRecipes = 10) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });
      
      const response = await axios.post('/api/scrape-recipes', {
        query: query || 'chicken recipes',
        max_recipes: maxRecipes
      });
      
      if (response.data.success) {
        dispatch({ type: 'SET_RECIPES', payload: response.data.recipes });
        dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const getRecipes = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const response = await axios.get('/api/recipes');
      
      if (response.data.success) {
        dispatch({ type: 'SET_RECIPES', payload: response.data.recipes });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const getUserIngredients = async () => {
    try {
      const response = await axios.get('/api/ingredients');
      
      if (response.data.success) {
        dispatch({ type: 'SET_USER_INGREDIENTS', payload: response.data.ingredients });
      }
    } catch (error) {
      console.error('Error fetching user ingredients:', error);
    }
  };

  const addUserIngredient = async (ingredient) => {
    try {
      const response = await axios.post('/api/ingredients', ingredient);
      
      if (response.data.success) {
        await getUserIngredients(); // Refresh the list
      }
    } catch (error) {
      console.error('Error adding ingredient:', error);
    }
  };

  const removeUserIngredient = async (ingredientId) => {
    try {
      // Note: You'll need to add a DELETE endpoint to your backend
      dispatch({ type: 'REMOVE_USER_INGREDIENT', payload: ingredientId });
    } catch (error) {
      console.error('Error removing ingredient:', error);
    }
  };

  const getRecipeNutrition = async (recipeId) => {
    try {
      const response = await axios.get(`/api/recipes/${recipeId}/nutrition`);
      
      if (response.data.success) {
        dispatch({ 
          type: 'SET_NUTRITION_DATA', 
          payload: { [recipeId]: response.data.nutrition } 
        });
      }
    } catch (error) {
      console.error('Error fetching nutrition data:', error);
    }
  };

  const saveRecipe = async (recipeId, rating = 5, notes = '') => {
    try {
      const response = await axios.post(`/api/recipes/${recipeId}/save`, {
        rating,
        notes
      });
      
      if (response.data.success) {
        // Find the recipe to save
        const recipe = state.recipes.find(r => r.id === recipeId);
        if (recipe) {
          dispatch({ 
            type: 'SAVE_RECIPE', 
            payload: { ...recipe, rating, notes } 
          });
        }
      }
    } catch (error) {
      console.error('Error saving recipe:', error);
    }
  };

  const swipeLeft = () => {
    dispatch({ type: 'SWIPE_LEFT' });
  };

  const swipeRight = () => {
    dispatch({ type: 'SWIPE_RIGHT' });
  };

  const nextRecipe = () => {
    dispatch({ type: 'NEXT_RECIPE' });
  };

  const previousRecipe = () => {
    dispatch({ type: 'PREVIOUS_RECIPE' });
  };

  // Load initial data
  useEffect(() => {
    getRecipes();
    getUserIngredients();
  }, []);

  const value = {
    ...state,
    scrapeRecipes,
    getRecipes,
    getUserIngredients,
    addUserIngredient,
    removeUserIngredient,
    getRecipeNutrition,
    saveRecipe,
    swipeLeft,
    swipeRight,
    nextRecipe,
    previousRecipe,
  };

  return (
    <RecipeContext.Provider value={value}>
      {children}
    </RecipeContext.Provider>
  );
};

export const useRecipe = () => {
  const context = useContext(RecipeContext);
  if (!context) {
    throw new Error('useRecipe must be used within a RecipeProvider');
  }
  return context;
};
