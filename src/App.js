import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import RecipeSwiper from './components/RecipeSwiper';
import IngredientManager from './components/IngredientManager';
import SavedRecipes from './components/SavedRecipes';
import RecipeDetail from './components/RecipeDetail';
import { RecipeProvider } from './context/RecipeContext';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('swiper');

  return (
    <RecipeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header currentView={currentView} setCurrentView={setCurrentView} />
          
          <main className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={
                <div className="space-y-6">
                  {currentView === 'swiper' && <RecipeSwiper />}
                  {currentView === 'ingredients' && <IngredientManager />}
                  {currentView === 'saved' && <SavedRecipes />}
                </div>
              } />
              <Route path="/recipe/:id" element={<RecipeDetail />} />
            </Routes>
          </main>
        </div>
      </Router>
    </RecipeProvider>
  );
}

export default App;
