import React from 'react';
import { ChefHat, ShoppingCart, Heart, Search } from 'lucide-react';

const Header = ({ currentView, setCurrentView }) => {
  const tabs = [
    { id: 'swiper', label: 'Discover', icon: Search, color: 'primary' },
    { id: 'ingredients', label: 'My Pantry', icon: ShoppingCart, color: 'secondary' },
    { id: 'saved', label: 'Saved', icon: Heart, color: 'pink' },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        {/* Main Header */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-500 p-2 rounded-lg">
              <ChefHat className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Spicerack</h1>
              <p className="text-sm text-gray-600">Discover • Swipe • Cook</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">Ready to cook?</p>
              <p className="text-lg font-semibold text-primary-600">Let's find recipes!</p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentView === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentView(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                  isActive
                    ? `bg-${tab.color}-500 text-white shadow-md`
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

export default Header;
