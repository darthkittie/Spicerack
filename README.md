# Spicerack 🍽️

A comprehensive recipe discovery and management application with web scraping, swipe gestures, ingredient tracking, and Instacart integration.

## ✨ Features

### 🔍 Recipe Discovery
- **Web Scraping**: Automatically scrapes recipes from popular cooking websites (AllRecipes, Food Network)
- **Smart Search**: Search for recipes by ingredients, cuisine, or dish type
- **Real-time Results**: Get fresh recipe suggestions instantly

### 👆 Swipe Interface
- **Tinder-style Swiping**: Swipe left to skip, right to save recipes
- **Touch & Mouse Support**: Works on both mobile and desktop
- **Smooth Animations**: Beautiful transitions and 3D card effects

### 🛒 Ingredient Management
- **Personal Pantry**: Track what ingredients you have at home
- **Smart Categorization**: Automatically categorizes ingredients (meat, dairy, produce, pantry)
- **Quantity Tracking**: Monitor ingredient amounts and units

### 🚚 Instacart Integration
- **Missing Ingredients**: Automatically identifies what you need to buy
- **Smart Checkout**: Creates Instacart cart with missing ingredients
- **Cost Estimation**: Shows estimated delivery costs and timing

### 📊 Nutrition Information
- **Macro Tracking**: Calories, protein, carbs, fat, fiber, and sugar
- **Smart Calculations**: Estimates nutrition based on ingredients
- **Visual Charts**: Easy-to-read nutrition displays

### 💾 Recipe Management
- **Save & Rate**: Save favorite recipes with personal ratings and notes
- **Organized Collections**: Browse and search through saved recipes
- **Detailed Views**: Full recipe instructions and ingredient lists

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Flask server**
   ```bash
   python app.py
   ```
   
   The backend will run on `n `

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Start the React development server**
   ```bash
   npm start
   ```
   
   The frontend will run on `http://localhost:3000`

## 🏗️ Architecture

### Backend (Python/Flask)
- **Web Scraping**: BeautifulSoup4 and Selenium for recipe extraction
- **Database**: SQLite for storing recipes, ingredients, and user data
- **APIs**: RESTful endpoints for all app functionality
- **Nutrition**: Smart nutrition calculation based on ingredients

### Frontend (React)
- **Modern UI**: Built with Tailwind CSS and Framer Motion
- **Responsive Design**: Works perfectly on all device sizes
- **State Management**: React Context for global state
- **Swipe Gestures**: React Swipeable for touch interactions

### Key Components
- `RecipeSwiper`: Main swiping interface
- `RecipeCard`: Individual recipe display
- `IngredientManager`: Pantry management
- `InstacartModal`: Shopping cart integration
- `SavedRecipes`: Recipe collection browser

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# API Keys (for future integrations)
NUTRITIONIX_API_KEY=your_key_here
INSTACART_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///recipes.db

# Server
FLASK_ENV=development
FLASK_DEBUG=True
```

### Customization
- **Recipe Sources**: Modify `app.py` to add more recipe websites
- **Nutrition API**: Replace mock nutrition data with real API integration
- **Instacart**: Implement actual Instacart API for real shopping cart creation

## 📱 Usage

### Discovering Recipes
1. Navigate to the "Discover" tab
2. Search for recipes or browse popular categories
3. Swipe right to save, left to skip
4. Use arrow buttons for precise navigation

### Managing Ingredients
1. Go to "My Pantry" tab
2. Add ingredients with quantities and units
3. View categorized ingredient overview
4. Track what you have vs. what you need

### Getting Missing Ingredients
1. Click "Get Ingredients" on any recipe
2. Review missing ingredients analysis
3. Click "Get from Instacart" to create shopping cart
4. Complete checkout on Instacart

### Saving Recipes
1. Swipe right or click save button
2. Rate the recipe (1-5 stars)
3. Add personal notes
4. Access saved recipes in the "Saved" tab

## 🎨 UI/UX Features

- **Modern Design**: Clean, intuitive interface with beautiful gradients
- **Smooth Animations**: Framer Motion animations for delightful interactions
- **Responsive Layout**: Adapts perfectly to all screen sizes
- **Accessibility**: High contrast, readable fonts, and keyboard navigation
- **Dark Mode Ready**: CSS variables for easy theme switching

## 🔮 Future Enhancements

- **Real Nutrition APIs**: Integration with Nutritionix or USDA databases
- **Recipe Recommendations**: AI-powered suggestions based on preferences
- **Meal Planning**: Weekly meal planning and grocery lists
- **Social Features**: Share recipes and cooking experiences
- **Voice Commands**: Voice-controlled recipe search and navigation
- **Offline Mode**: Cache recipes for offline browsing
- **Multi-language**: Support for international cuisines

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version (3.8+ required)
- Install all dependencies: `pip install -r requirements.txt`
- Ensure port 5000 is available

**Frontend won't start**
- Check Node.js version (16+ required)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**Web scraping issues**
- Some websites may block automated requests
- Check internet connection
- Verify website structure hasn't changed

**Database errors**
- Delete `recipes.db` file to reset database
- Check file permissions in project directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Recipe Sources**: AllRecipes, Food Network for recipe content
- **UI Libraries**: Tailwind CSS, Framer Motion, Lucide React
- **Backend Tools**: Flask, BeautifulSoup4, SQLite
- **Frontend Framework**: React with modern hooks and context

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the code comments for implementation details

---

**Happy Cooking! 🍳✨**
