from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            nutrition_info TEXT,
            image_url TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_name TEXT NOT NULL,
            quantity TEXT,
            unit TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            user_rating INTEGER,
            notes TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Recipe Tracker API is running'})

@app.route('/api/scrape-recipes', methods=['POST'])
def scrape_recipes():
    try:
        data = request.get_json()
        query = data.get('query', 'chicken recipes')
        max_recipes = data.get('max_recipes', 10)
        
        print(f"Scraping recipes for query: {query}")
        
        # Scrape recipes from multiple sources
        recipes = []
        
        # AllRecipes scraping
        print("Scraping AllRecipes...")
        allrecipes_recipes = scrape_allrecipes(query, max_recipes // 2)
        print(f"Found {len(allrecipes_recipes)} recipes from AllRecipes")
        recipes.extend(allrecipes_recipes)
        
        # Food Network scraping
        print("Scraping Food Network...")
        foodnetwork_recipes = scrape_foodnetwork(query, max_recipes // 2)
        print(f"Found {len(foodnetwork_recipes)} recipes from Food Network")
        recipes.extend(foodnetwork_recipes)
        
        # If no recipes found from scraping, provide fallback data
        if len(recipes) == 0:
            print("No recipes found from scraping, providing fallback data...")
            recipes = get_fallback_recipes(query, max_recipes)
        
        # Save recipes to database
        saved_recipes = []
        for recipe in recipes:
            recipe_id = save_recipe_to_db(recipe)
            recipe['id'] = recipe_id
            saved_recipes.append(recipe)
        
        print(f"Total recipes saved: {len(saved_recipes)}")
        
        return jsonify({
            'success': True,
            'recipes': saved_recipes,
            'total_found': len(saved_recipes)
        })
        
    except Exception as e:
        print(f"Error in scrape_recipes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def scrape_allrecipes(query, max_recipes):
    recipes = []
    try:
        # Search AllRecipes
        search_url = f"https://www.allrecipes.com/search?q={query.replace(' ', '+')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"Searching AllRecipes: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"AllRecipes response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"AllRecipes returned status {response.status_code}")
            return recipes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for recipe cards
        recipe_cards = []
        selectors = [
            'div[class*="card__detailsContainer"]',
            'div[class*="recipe-card"]',
            'div[class*="search-result"]',
            'article[class*="recipe"]',
            'div[class*="recipe-item"]'
        ]
        
        for selector in selectors:
            recipe_cards = soup.select(selector)
            if recipe_cards:
                print(f"Found {len(recipe_cards)} recipe cards using selector: {selector}")
                break
        
        if not recipe_cards:
            print("No recipe cards found with any selector")
            # Try to find any links that might be recipes
            recipe_links = soup.find_all('a', href=re.compile(r'/recipe/'))
            print(f"Found {len(recipe_links)} potential recipe links")
            if recipe_links:
                recipe_cards = recipe_links[:max_recipes]
        
        recipe_cards = recipe_cards[:max_recipes]
        
        for i, card in enumerate(recipe_cards):
            try:
                print(f"Processing recipe card {i+1}/{len(recipe_cards)}")
                
                # Try different ways to extract title and link
                title = None
                recipe_url = None
                
                # Method 1: Look for title in h3 or similar elements
                title_elem = card.find(['h3', 'h2', 'h1'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                
                # Method 2: Look for title in class names
                if not title:
                    title_elem = card.find(class_=re.compile(r'title|headline|name'))
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                # Method 3: Look for title in any text content
                if not title:
                    title = card.get_text(strip=True)[:100]  # First 100 chars
                
                # Find recipe URL
                if card.name == 'a':
                    recipe_url = card.get('href')
                else:
                    link_elem = card.find('a')
                    if link_elem:
                        recipe_url = link_elem.get('href')
                
                # Make URL absolute
                if recipe_url and not recipe_url.startswith('http'):
                    if recipe_url.startswith('/'):
                        recipe_url = 'https://www.allrecipes.com' + recipe_url
                    else:
                        recipe_url = 'https://www.allrecipes.com/' + recipe_url
                
                print(f"Title: {title}")
                print(f"URL: {recipe_url}")
                
                if recipe_url and title:
                    # Get detailed recipe info
                    recipe_details = get_recipe_details(recipe_url, headers)
                    if recipe_details:
                        recipes.append(recipe_details)
                        print(f"Successfully added recipe: {recipe_details['title']}")
                    else:
                        print(f"Failed to get details for: {title}")
                        
            except Exception as e:
                print(f"Error processing recipe card {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping AllRecipes: {e}")
    
    print(f"AllRecipes scraping completed. Found {len(recipes)} recipes.")
    return recipes

def scrape_foodnetwork(query, max_recipes):
    recipes = []
    try:
        # Search Food Network
        search_url = f"https://www.foodnetwork.com/search/{query.replace(' ', '-')}-"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"Searching Food Network: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"Food Network response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Food Network returned status {response.status_code}")
            return recipes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for recipe cards
        recipe_cards = []
        selectors = [
            'div[class*="o-ResultCard"]',
            'div[class*="recipe-card"]',
            'div[class*="search-result"]',
            'article[class*="recipe"]',
            'div[class*="recipe-item"]',
            'div[class*="card"]'
        ]
        
        for selector in selectors:
            recipe_cards = soup.select(selector)
            if recipe_cards:
                print(f"Found {len(recipe_cards)} recipe cards using selector: {selector}")
                break
        
        if not recipe_cards:
            print("No recipe cards found with any selector")
            # Try to find any links that might be recipes
            recipe_links = soup.find_all('a', href=re.compile(r'/recipes/'))
            print(f"Found {len(recipe_links)} potential recipe links")
            if recipe_links:
                recipe_cards = recipe_links[:max_recipes]
        
        recipe_cards = recipe_cards[:max_recipes]
        
        for i, card in enumerate(recipe_cards):
            try:
                print(f"Processing Food Network recipe card {i+1}/{len(recipe_cards)}")
                
                # Try different ways to extract title and link
                title = None
                recipe_url = None
                
                # Method 1: Look for title in h3 or similar elements
                title_elem = card.find(['h3', 'h2', 'h1'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                
                # Method 2: Look for title in class names
                if not title:
                    title_elem = card.find(class_=re.compile(r'title|headline|name'))
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                # Method 3: Look for title in any text content
                if not title:
                    title = card.get_text(strip=True)[:100]  # First 100 chars
                
                # Find recipe URL
                if card.name == 'a':
                    recipe_url = card.get('href')
                else:
                    link_elem = card.find('a')
                    if link_elem:
                        recipe_url = link_elem.get('href')
                
                # Make URL absolute
                if recipe_url and not recipe_url.startswith('http'):
                    if recipe_url.startswith('/'):
                        recipe_url = 'https://www.foodnetwork.com' + recipe_url
                    else:
                        recipe_url = 'https://www.foodnetwork.com/' + recipe_url
                
                print(f"Title: {title}")
                print(f"URL: {recipe_url}")
                
                if recipe_url and title:
                    # Get detailed recipe info
                    recipe_details = get_recipe_details(recipe_url, headers)
                    if recipe_details:
                        recipes.append(recipe_details)
                        print(f"Successfully added recipe: {recipe_details['title']}")
                    else:
                        print(f"Failed to get details for: {title}")
                        
            except Exception as e:
                print(f"Error processing Food Network recipe card {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping Food Network: {e}")
    
    print(f"Food Network scraping completed. Found {len(recipes)} recipes.")
    return recipes

def get_recipe_details(url, headers):
    try:
        print(f"Getting recipe details from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to get recipe page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract recipe information
        title = None
        
        # Try multiple selectors for title
        title_selectors = [
            'h1',
            'h1[class*="title"]',
            'h1[class*="recipe"]',
            'h1[class*="headline"]',
            'h2[class*="title"]',
            'h2[class*="recipe"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        if not title:
            title = 'Unknown Recipe'
        
        print(f"Extracted title: {title}")
        
        # Extract ingredients
        ingredients = []
        ingredient_selectors = [
            '[class*="ingredient"]',
            '[class*="ingredients"]',
            'li[class*="ingredient"]',
            'span[class*="ingredient"]',
            'div[class*="ingredient"]'
        ]
        
        for selector in ingredient_selectors:
            ingredient_elements = soup.select(selector)
            if ingredient_elements:
                for elem in ingredient_elements:
                    ingredient_text = elem.get_text(strip=True)
                    if ingredient_text and len(ingredient_text) > 3 and ingredient_text not in ingredients:
                        ingredients.append(ingredient_text)
                if ingredients:
                    break
        
        # If no ingredients found, try a more generic approach
        if not ingredients:
            # Look for lists that might contain ingredients
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) > 5 and len(text) < 200 and not any(word in text.lower() for word in ['step', 'instruction', 'direction', 'preheat', 'heat']):
                        ingredients.append(text)
        
        print(f"Extracted {len(ingredients)} ingredients")
        
        # Extract instructions
        instructions = []
        instruction_selectors = [
            '[class*="instruction"]',
            '[class*="directions"]',
            '[class*="steps"]',
            '[class*="method"]',
            'li[class*="step"]',
            'p[class*="instruction"]'
        ]
        
        for selector in instruction_selectors:
            instruction_elements = soup.select(selector)
            if instruction_elements:
                for elem in instruction_elements:
                    instruction_text = elem.get_text(strip=True)
                    if instruction_text and len(instruction_text) > 10 and instruction_text not in instructions:
                        instructions.append(instruction_text)
                if instructions:
                    break
        
        # If no instructions found, try a more generic approach
        if not instructions:
            # Look for paragraphs that might contain instructions
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 500 and any(word in text.lower() for word in ['preheat', 'heat', 'cook', 'add', 'stir', 'mix', 'bake', 'grill']):
                    instructions.append(text)
        
        print(f"Extracted {len(ingredients)} instructions")
        
        # Extract image
        image_url = None
        image_selectors = [
            'img[class*="recipe"]',
            'img[class*="food"]',
            'img[class*="hero"]',
            'img[class*="main"]',
            'img[class*="featured"]'
        ]
        
        for selector in image_selectors:
            image_elem = soup.select_one(selector)
            if image_elem and image_elem.get('src'):
                image_url = image_elem['src']
                break
        
        # If no specific image found, try to find any image
        if not image_url:
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src and ('food' in src.lower() or 'recipe' in src.lower() or 'dish' in src.lower()):
                    image_url = src
                    break
        
        # Make image URL absolute if it's relative
        if image_url and not image_url.startswith('http'):
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])  # Get domain
                image_url = base_url + image_url
            else:
                base_url = '/'.join(url.split('/')[:-1])  # Get directory
                image_url = base_url + '/' + image_url
        
        print(f"Extracted image: {image_url}")
        
        # If we don't have enough data, return None
        if len(ingredients) < 2 or len(instructions) < 1:
            print(f"Insufficient data: {len(ingredients)} ingredients, {len(instructions)} instructions")
            return None
        
        return {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'image_url': image_url,
            'source_url': url
        }
        
    except Exception as e:
        print(f"Error getting recipe details from {url}: {e}")
        return None

def save_recipe_to_db(recipe):
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO recipes (title, ingredients, instructions, image_url, source_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        recipe['title'],
        json.dumps(recipe['ingredients']),
        json.dumps(recipe['instructions']),
        recipe.get('image_url'),
        recipe.get('source_url')
    ))
    
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return recipe_id

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    try:
        conn = sqlite3.connect('recipes.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recipes ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        recipes = []
        for row in rows:
            recipes.append({
                'id': row[0],
                'title': row[1],
                'ingredients': json.loads(row[2]),
                'instructions': json.loads(row[3]),
                'nutrition_info': row[4],
                'image_url': row[5],
                'source_url': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return jsonify({'success': True, 'recipes': recipes})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>/nutrition', methods=['GET'])
def get_recipe_nutrition(recipe_id):
    try:
        conn = sqlite3.connect('recipes.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT ingredients FROM recipes WHERE id = ?', (recipe_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'Recipe not found'}), 404
        
        ingredients = json.loads(row[0])
        
        # Get nutrition data from Nutritionix API
        nutrition_data = get_nutrition_data(ingredients)
        
        # Update recipe with nutrition info
        conn = sqlite3.connect('recipes.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE recipes SET nutrition_info = ? WHERE id = ?', 
                      (json.dumps(nutrition_data), recipe_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'nutrition': nutrition_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_nutrition_data(ingredients):
    # This would integrate with a real nutrition API like Nutritionix
    # For now, returning mock data
    nutrition = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0
    }
    
    # Mock calculation based on ingredients
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        if 'chicken' in ingredient_lower or 'beef' in ingredient_lower:
            nutrition['protein'] += 25
            nutrition['calories'] += 150
        elif 'rice' in ingredient_lower or 'pasta' in ingredient_lower:
            nutrition['carbs'] += 45
            nutrition['calories'] += 200
        elif 'oil' in ingredient_lower or 'butter' in ingredient_lower:
            nutrition['fat'] += 14
            nutrition['calories'] += 120
        elif 'vegetable' in ingredient_lower or 'salad' in ingredient_lower:
            nutrition['fiber'] += 3
            nutrition['calories'] += 30
    
    return nutrition

@app.route('/api/ingredients', methods=['GET', 'POST'])
def manage_ingredients():
    if request.method == 'GET':
        try:
            conn = sqlite3.connect('recipes.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_ingredients ORDER BY added_at DESC')
            rows = cursor.fetchall()
            
            ingredients = []
            for row in rows:
                ingredients.append({
                    'id': row[0],
                    'ingredient_name': row[1],
                    'quantity': row[2],
                    'unit': row[3],
                    'added_at': row[4]
                })
            
            conn.close()
            return jsonify({'success': True, 'ingredients': ingredients})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            ingredient_name = data.get('ingredient_name')
            quantity = data.get('quantity', '1')
            unit = data.get('unit', 'piece')
            
            conn = sqlite3.connect('recipes.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_ingredients (ingredient_name, quantity, unit)
                VALUES (?, ?, ?)
            ''', (ingredient_name, quantity, unit))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Ingredient added successfully'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/instacart/checkout', methods=['POST'])
def instacart_checkout():
    try:
        data = request.get_json()
        missing_ingredients = data.get('missing_ingredients', [])
        
        # This would integrate with Instacart's API
        # For now, returning mock response
        checkout_data = {
            'cart_id': 'mock_cart_123',
            'total_items': len(missing_ingredients),
            'estimated_total': len(missing_ingredients) * 5.99,
            'delivery_estimate': '2-4 hours',
            'checkout_url': 'https://instacart.com/checkout/mock_cart_123'
        }
        
        return jsonify({
            'success': True,
            'checkout': checkout_data,
            'message': 'Instacart integration would be implemented here'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>/save', methods=['POST'])
def save_recipe(recipe_id):
    try:
        data = request.get_json()
        rating = data.get('rating', 5)
        notes = data.get('notes', '')
        
        conn = sqlite3.connect('recipes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO saved_recipes (recipe_id, user_rating, notes)
            VALUES (?, ?, ?)
        ''', (recipe_id, rating, notes))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Recipe saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_fallback_recipes(query, max_recipes):
    """Provide fallback recipe data when web scraping fails"""
    fallback_recipes = [
        {
            'title': 'Grilled Chicken Breast',
            'ingredients': [
                '4 boneless, skinless chicken breasts',
                '2 tablespoons olive oil',
                '1 teaspoon salt',
                '1/2 teaspoon black pepper',
                '1 teaspoon garlic powder',
                '1 teaspoon dried oregano'
            ],
            'instructions': [
                'Preheat grill to medium-high heat',
                'Brush chicken breasts with olive oil',
                'Season with salt, pepper, garlic powder, and oregano',
                'Grill for 6-8 minutes per side until internal temperature reaches 165°F',
                'Let rest for 5 minutes before serving'
            ],
            'image_url': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400',
            'source_url': 'https://example.com/grilled-chicken-breast'
        },
        {
            'title': 'Creamy Pasta with Chicken',
            'ingredients': [
                '1 pound fettuccine pasta',
                '2 boneless, skinless chicken breasts, cubed',
                '2 tablespoons butter',
                '2 cloves garlic, minced',
                '1 cup heavy cream',
                '1/2 cup grated Parmesan cheese',
                'Salt and pepper to taste',
                'Fresh parsley for garnish'
            ],
            'instructions': [
                'Cook pasta according to package directions',
                'Season chicken with salt and pepper',
                'In a large skillet, melt butter over medium heat',
                'Add chicken and cook until golden brown, about 5-7 minutes',
                'Add garlic and cook for 1 minute',
                'Pour in heavy cream and bring to a simmer',
                'Stir in Parmesan cheese until melted',
                'Add cooked pasta and toss to combine',
                'Garnish with fresh parsley and serve'
            ],
            'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=400',
            'source_url': 'https://example.com/creamy-pasta-chicken'
        },
        {
            'title': 'Chicken Stir Fry',
            'ingredients': [
                '1 pound boneless, skinless chicken breast, sliced',
                '2 tablespoons soy sauce',
                '1 tablespoon cornstarch',
                '2 tablespoons vegetable oil',
                '2 cups mixed vegetables (broccoli, bell peppers, carrots)',
                '3 cloves garlic, minced',
                '1 tablespoon ginger, minced',
                '2 tablespoons oyster sauce',
                '1/4 cup chicken broth'
            ],
            'instructions': [
                'Slice chicken and marinate with soy sauce and cornstarch for 15 minutes',
                'Heat oil in a wok or large skillet over high heat',
                'Add chicken and stir-fry until cooked through, about 5 minutes',
                'Remove chicken and set aside',
                'Add vegetables, garlic, and ginger to the wok',
                'Stir-fry vegetables for 3-4 minutes',
                'Return chicken to the wok',
                'Add oyster sauce and chicken broth',
                'Stir-fry for 2 minutes until sauce thickens',
                'Serve hot over rice'
            ],
            'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400',
            'source_url': 'https://example.com/chicken-stir-fry'
        }
    ]
    
    # Filter recipes based on query if possible
    if 'chicken' in query.lower():
        return fallback_recipes[:max_recipes]
    elif 'pasta' in query.lower():
        return [fallback_recipes[1]] if max_recipes >= 1 else []
    elif 'stir' in query.lower() or 'asian' in query.lower():
        return [fallback_recipes[2]] if max_recipes >= 1 else []
    else:
        return fallback_recipes[:max_recipes]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
