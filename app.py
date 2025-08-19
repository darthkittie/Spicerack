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
import time  # Add this import for delays

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
    return jsonify({'status': 'healthy', 'message': 'Spicerack API is running'})

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
        foodnetwork_recipes = scrape_foodnetwork(query, max_recipes // 3)
        print(f"Found {len(foodnetwork_recipes)} recipes from Food Network")
        recipes.extend(foodnetwork_recipes)
        
        # Epicurious scraping
        print("Scraping Epicurious...")
        epicurious_recipes = scrape_epicurious(query, max_recipes // 3)
        print(f"Found {len(epicurious_recipes)} recipes from Epicurious")
        recipes.extend(epicurious_recipes)
        
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"Searching AllRecipes: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"AllRecipes response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"AllRecipes returned status {response.status_code}")
            return recipes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for recipe cards - updated for current AllRecipes structure
        recipe_cards = []
        selectors = [
            'a[href*="/recipe/"]',  # Direct recipe links
            'div[class*="card__detailsContainer"]',
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
                
                # Find recipe URL - improved logic
                if card.name == 'a':
                    recipe_url = card.get('href')
                else:
                    link_elem = card.find('a')
                    if link_elem:
                        recipe_url = link_elem.get('href')
                
                # Make URL absolute and clean it
                if recipe_url:
                    if not recipe_url.startswith('http'):
                        if recipe_url.startswith('/'):
                            recipe_url = 'https://www.allrecipes.com' + recipe_url
                        else:
                            recipe_url = 'https://www.allrecipes.com/' + recipe_url
                    
                    # Only process if it's actually a recipe URL
                    if '/recipe/' not in recipe_url:
                        continue
                
                print(f"Title: {title}")
                print(f"URL: {recipe_url}")
                
                if recipe_url and title and '/recipe/' in recipe_url:
                    # Get detailed recipe info
                    recipe_details = get_recipe_details(recipe_url, headers)
                    if recipe_details:
                        recipes.append(recipe_details)
                        print(f"Successfully added recipe: {recipe_details['title']}")
                    else:
                        print(f"Failed to get details for: {title}")
                    
                    # Add a small delay to be respectful to the website
                    time.sleep(1)
                        
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"Searching Food Network: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"Food Network response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Food Network returned status {response.status_code}")
            return recipes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for recipe cards - updated for current Food Network structure
        recipe_cards = []
        selectors = [
            'a[href*="/recipes/"]',  # Direct recipe links
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
                
                # Find recipe URL - improved logic
                if card.name == 'a':
                    recipe_url = card.get('href')
                else:
                    link_elem = card.find('a')
                    if link_elem:
                        recipe_url = link_elem.get('href')
                
                # Make URL absolute and clean it
                if recipe_url:
                    if not recipe_url.startswith('http'):
                        if recipe_url.startswith('/'):
                            recipe_url = 'https://www.foodnetwork.com' + recipe_url
                        else:
                            recipe_url = 'https://www.foodnetwork.com/' + recipe_url
                    
                    # Only process if it's actually a recipe URL
                    if '/recipes/' not in recipe_url:
                        continue
                
                print(f"Title: {title}")
                print(f"URL: {recipe_url}")
                
                if recipe_url and title and '/recipes/' in recipe_url:
                    # Get detailed recipe info
                    recipe_details = get_recipe_details(recipe_url, headers)
                    if recipe_details:
                        recipes.append(recipe_details)
                        print(f"Successfully added recipe: {recipe_details['title']}")
                    else:
                        print(f"Failed to get details for: {title}")
                    
                    # Add a small delay to be respectful to the website
                    time.sleep(1)
                        
            except Exception as e:
                print(f"Error processing Food Network recipe card {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping Food Network: {e}")
    
    print(f"Food Network scraping completed. Found {len(recipes)} recipes.")
    return recipes

def scrape_epicurious(query, max_recipes):
    recipes = []
    try:
        # Search Epicurious
        search_url = f"https://www.epicurious.com/search/{query.replace(' ', '-')}-"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"Searching Epicurious: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"Epicurious response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Epicurious returned status {response.status_code}")
            return recipes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for recipe cards - updated for current Epicurious structure
        recipe_cards = []
        selectors = [
            'a[href*="/recipes/"]',  # Direct recipe links
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
                print(f"Processing Epicurious recipe card {i+1}/{len(recipe_cards)}")
                
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
                
                # Find recipe URL - improved logic
                if card.name == 'a':
                    recipe_url = card.get('href')
                else:
                    link_elem = card.find('a')
                    if link_elem:
                        recipe_url = link_elem.get('href')
                
                # Make URL absolute and clean it
                if recipe_url:
                    if not recipe_url.startswith('http'):
                        if recipe_url.startswith('/'):
                            recipe_url = 'https://www.epicurious.com' + recipe_url
                        else:
                            recipe_url = 'https://www.epicurious.com/' + recipe_url
                    
                    # Only process if it's actually a recipe URL
                    if '/recipes/' not in recipe_url:
                        continue
                
                print(f"Title: {title}")
                print(f"URL: {recipe_url}")
                
                if recipe_url and title and '/recipes/' in recipe_url:
                    # Get detailed recipe info
                    recipe_details = get_recipe_details(recipe_url, headers)
                    if recipe_details:
                        recipes.append(recipe_details)
                        print(f"Successfully added recipe: {recipe_details['title']}")
                    else:
                        print(f"Failed to get details for: {title}")
                    
                    # Add a small delay to be respectful to the website
                    time.sleep(1)
                        
            except Exception as e:
                print(f"Error processing Epicurious recipe card {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping Epicurious: {e}")
    
    print(f"Epicurious scraping completed. Found {len(recipes)} recipes.")
    return recipes

def get_recipe_details(url, headers):
    try:
        print(f"Getting recipe details from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Failed to get recipe page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract recipe information
        title = None
        
        # Try multiple selectors for title - expanded for better coverage
        title_selectors = [
            'h1',
            'h1[class*="title"]',
            'h1[class*="recipe"]',
            'h1[class*="headline"]',
            'h1[class*="main"]',
            'h2[class*="title"]',
            'h2[class*="recipe"]',
            'h2[class*="headline"]',
            'h3[class*="title"]',
            'h3[class*="recipe"]',
            '[class*="recipe-title"]',
            '[class*="recipe-headline"]',
            '[class*="main-title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    break
        
        if not title:
            title = 'Unknown Recipe'
        
        print(f"Extracted title: {title}")
        
        # Extract ingredients - improved selectors
        ingredients = []
        ingredient_selectors = [
            '[class*="ingredient"]',
            '[class*="ingredients"]',
            'li[class*="ingredient"]',
            'span[class*="ingredient"]',
            'div[class*="ingredient"]',
            '[class*="ingredients-list"] li',
            '[class*="ingredient-list"] li',
            '[class*="recipe-ingredients"] li'
        ]
        
        for selector in ingredient_selectors:
            ingredient_elements = soup.select(selector)
            if ingredient_elements:
                for elem in ingredient_elements:
                    ingredient_text = elem.get_text(strip=True)
                    if ingredient_text and len(ingredient_text) > 3 and len(ingredient_text) < 200:
                        # Clean up the ingredient text
                        clean_text = re.sub(r'\s+', ' ', ingredient_text).strip()
                        if clean_text and clean_text not in ingredients:
                            ingredients.append(clean_text)
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
                    if text and len(text) > 5 and len(text) < 200:
                        # Check if this looks like an ingredient
                        text_lower = text.lower()
                        if not any(word in text_lower for word in ['step', 'instruction', 'direction', 'preheat', 'heat', 'cook', 'bake', 'grill', 'fry', 'simmer', 'boil']):
                            clean_text = re.sub(r'\s+', ' ', text).strip()
                            if clean_text and clean_text not in ingredients:
                                ingredients.append(clean_text)
        
        print(f"Extracted {len(ingredients)} ingredients")
        
        # Extract instructions - improved selectors
        instructions = []
        instruction_selectors = [
            '[class*="instruction"]',
            '[class*="directions"]',
            '[class*="steps"]',
            '[class*="method"]',
            'li[class*="step"]',
            'p[class*="instruction"]',
            '[class*="recipe-instructions"] li',
            '[class*="recipe-directions"] li',
            '[class*="cooking-steps"] li'
        ]
        
        for selector in instruction_selectors:
            instruction_elements = soup.select(selector)
            if instruction_elements:
                for elem in instruction_elements:
                    instruction_text = elem.get_text(strip=True)
                    if instruction_text and len(instruction_text) > 10 and len(instruction_text) < 500:
                        clean_text = re.sub(r'\s+', ' ', instruction_text).strip()
                        if clean_text and clean_text not in instructions:
                            instructions.append(clean_text)
                if instructions:
                    break
        
        # If no instructions found, try a more generic approach
        if not instructions:
            # Look for paragraphs that might contain instructions
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 500:
                    text_lower = text.lower()
                    if any(word in text_lower for word in ['preheat', 'heat', 'cook', 'add', 'stir', 'mix', 'bake', 'grill', 'fry', 'simmer', 'boil', 'season', 'combine']):
                        clean_text = re.sub(r'\s+', ' ', text).strip()
                        if clean_text and clean_text not in instructions:
                            instructions.append(clean_text)
        
        print(f"Extracted {len(instructions)} instructions")
        
        # Extract image - enhanced selectors for better image quality
        image_url = None
        image_selectors = [
            # High priority - recipe-specific images
            'img[class*="recipe"]',
            'img[class*="food"]',
            'img[class*="hero"]',
            'img[class*="main"]',
            'img[class*="featured"]',
            'img[class*="primary"]',
            'img[class*="lead"]',
            '[class*="recipe-image"] img',
            '[class*="hero-image"] img',
            '[class*="main-image"] img',
            '[class*="featured-image"] img',
            '[class*="lead-image"] img',
            # Medium priority - general content images
            'img[class*="content"]',
            'img[class*="article"]',
            'img[class*="post"]',
            '[class*="content-image"] img',
            '[class*="article-image"] img',
            # Low priority - any image with food-related attributes
            'img[alt*="recipe"]',
            'img[alt*="food"]',
            'img[alt*="dish"]',
            'img[alt*="cooking"]',
            'img[alt*="meal"]'
        ]
        
        # Try to find the best quality image
        best_image = None
        best_score = 0
        
        for selector in image_selectors:
            image_elements = soup.select(selector)
            for img in image_elements:
                src = img.get('src')
                if not src:
                    continue
                
                # Score the image based on various factors
                score = 0
                
                # Higher score for larger images (check width/height attributes)
                width = img.get('width') or img.get('data-width')
                height = img.get('height') or img.get('data-height')
                if width and height:
                    try:
                        w, h = int(width), int(height)
                        if w >= 400 and h >= 300:  # Good size
                            score += 10
                        elif w >= 300 and h >= 200:  # Acceptable size
                            score += 5
                    except ValueError:
                        pass
                
                # Higher score for images with descriptive alt text
                alt = img.get('alt', '').lower()
                if any(word in alt for word in ['recipe', 'food', 'dish', 'cooking', 'meal', 'delicious']):
                    score += 8
                
                # Higher score for images with specific classes
                img_class = img.get('class', [])
                if any('recipe' in cls.lower() for cls in img_class):
                    score += 6
                if any('hero' in cls.lower() or 'main' in cls.lower() for cls in img_class):
                    score += 4
                
                # Higher score for images that are likely the main image
                if img.find_parent(['header', 'article', 'main']):
                    score += 3
                
                # Check if this is a better image than what we have
                if score > best_score:
                    best_score = score
                    best_image = img
        
        # Use the best image found, or fall back to simpler selection
        if best_image and best_image.get('src'):
            image_url = best_image['src']
        else:
            # Fallback: try to find any reasonable image
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src and len(src) > 10:  # Avoid very short URLs
                    # Skip common non-recipe images
                    skip_patterns = ['logo', 'icon', 'avatar', 'banner', 'ad', 'sponsor']
                    if not any(pattern in src.lower() for pattern in skip_patterns):
                        image_url = src
                        break
        
        # Make image URL absolute if it's relative
        if image_url:
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])  # Get domain
                image_url = base_url + image_url
            elif not image_url.startswith('http'):
                base_url = '/'.join(url.split('/')[:-1])  # Get directory
                image_url = base_url + '/' + image_url
            
            # Clean up the URL (remove query parameters that might cause issues)
            if '?' in image_url:
                base_img_url = image_url.split('?')[0]
                # Keep the URL if it looks like a proper image
                if any(ext in base_img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                    image_url = base_img_url
        
        # Site-specific image extraction fallbacks
        if not image_url:
            domain = url.lower()
            if 'allrecipes.com' in domain:
                # AllRecipes specific selectors
                allrecipes_selectors = [
                    'img[data-src*="recipe"]',
                    'img[data-src*="food"]',
                    'img[data-lazy-src]',
                    '[class*="lead-media"] img',
                    '[class*="recipe-media"] img'
                ]
                for selector in allrecipes_selectors:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        src = img_elem.get('data-src') or img_elem.get('data-lazy-src') or img_elem.get('src')
                        if src:
                            image_url = src
                            break
                            
            elif 'foodnetwork.com' in domain:
                # Food Network specific selectors
                foodnetwork_selectors = [
                    'img[data-src*="recipe"]',
                    'img[data-src*="food"]',
                    '[class*="lead-media"] img',
                    '[class*="recipe-media"] img',
                    '[class*="hero-media"] img'
                ]
                for selector in foodnetwork_selectors:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        src = img_elem.get('data-src') or img_elem.get('src')
                        if src:
                            image_url = src
                            break
                            
            elif 'epicurious.com' in domain:
                # Epicurious specific selectors
                epicurious_selectors = [
                    'img[data-src*="recipe"]',
                    'img[data-src*="food"]',
                    '[class*="lead-media"] img',
                    '[class*="recipe-media"] img',
                    '[class*="hero-media"] img'
                ]
                for selector in epicurious_selectors:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        src = img_elem.get('data-src') or img_elem.get('src')
                        if src:
                            image_url = src
                            break
            
            # Make the site-specific image URL absolute if needed
            if image_url and not image_url.startswith('http'):
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    base_url = '/'.join(url.split('/')[:3])
                    image_url = base_url + image_url
                else:
                    base_url = '/'.join(url.split('/')[:-1])
                    image_url = base_url + '/' + image_url
        
        # Additional fallback: Look for images in meta tags (Open Graph, Twitter Cards)
        if not image_url:
            meta_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'meta[property="og:image:secure_url"]',
                'meta[name="image"]'
            ]
            for selector in meta_selectors:
                meta_elem = soup.select_one(selector)
                if meta_elem:
                    content = meta_elem.get('content')
                    if content and content.startswith(('http://', 'https://')):
                        image_url = content
                        print(f"Found image in meta tag: {image_url}")
                        break
        
        # Additional fallback: Look for images in JSON-LD structured data
        if not image_url:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        # Look for image in various JSON-LD structures
                        if 'image' in json_data:
                            if isinstance(json_data['image'], str):
                                image_url = json_data['image']
                                break
                            elif isinstance(json_data['image'], dict) and 'url' in json_data['image']:
                                image_url = json_data['image']['url']
                                break
                            elif isinstance(json_data['image'], list) and len(json_data['image']) > 0:
                                if isinstance(json_data['image'][0], str):
                                    image_url = json_data['image'][0]
                                    break
                                elif isinstance(json_data['image'][0], dict) and 'url' in json_data['image'][0]:
                                    image_url = json_data['image'][0]['url']
                                    break
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        
        print(f"Extracted image: {image_url}")
        
        # Optimize the image URL for better performance
        if image_url:
            image_url = validate_and_optimize_image_url(image_url)
            print(f"Optimized image URL: {image_url}")
            
            # Test if the image URL is actually accessible
            if not test_image_url(image_url):
                print(f"Image URL not accessible, using fallback: {image_url}")
                image_url = get_fallback_image_url(title, ingredients)
        else:
            # Provide a fallback image based on recipe content
            image_url = get_fallback_image_url(title, ingredients)
            print(f"Using fallback image: {image_url}")
        
        # If we don't have enough data, return None
        if len(ingredients) < 2 or len(instructions) < 1:
            print(f"Insufficient data: {len(ingredients)} ingredients, {len(instructions)} instructions")
            return None
        
        return {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'image_url': image_url,
            'source_url': url  # This will be the actual recipe URL, not example.com
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

def validate_and_optimize_image_url(image_url):
    """Validate image URL and potentially optimize it for better performance"""
    if not image_url:
        return None
    
    try:
        # Check if the URL is valid
        if not image_url.startswith(('http://', 'https://')):
            return None
        
        # For some sites, we can optimize the image URL for better performance
        domain = image_url.lower()
        
        # AllRecipes image optimization
        if 'allrecipes.com' in domain:
            # AllRecipes often supports size parameters
            if '?' not in image_url:
                image_url += '?w=400&h=300&fit=crop'
            elif 'w=' not in image_url:
                image_url += '&w=400&h=300&fit=crop'
        
        # Food Network image optimization
        elif 'foodnetwork.com' in domain:
            # Food Network often supports size parameters
            if '?' not in image_url:
                image_url += '?w=400&h=300&fit=crop'
            elif 'w=' not in image_url:
                image_url += '&w=400&h=300&fit=crop'
        
        # Epicurious image optimization
        elif 'epicurious.com' in domain:
            # Epicurious often supports size parameters
            if '?' not in image_url:
                image_url += '?w=400&h=300&fit=crop'
            elif 'w=' not in image_url:
                image_url += '&w=400&h=300&fit=crop'
        
        # Generic image optimization for common image services
        elif any(service in domain for service in ['unsplash.com', 'pexels.com', 'pixabay.com']):
            # These services often support size parameters
            if '?' not in image_url:
                image_url += '?w=400&h=300&fit=crop'
            elif 'w=' not in image_url:
                image_url += '&w=400&h=300&fit=crop'
        
        return image_url
        
    except Exception as e:
        print(f"Error optimizing image URL {image_url}: {e}")
        return image_url  # Return original URL if optimization fails

def get_fallback_image_url(title, ingredients):
    """Get a relevant fallback image based on recipe content"""
    try:
        # Convert to lowercase for easier matching
        title_lower = title.lower()
        ingredients_lower = [ing.lower() for ing in ingredients]
        all_text = title_lower + ' ' + ' '.join(ingredients_lower)
        
        # Define fallback images for different food categories
        fallback_images = {
            # Chicken dishes
            'chicken': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=300&fit=crop',
            # Pasta dishes
            'pasta': 'https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=400&h=300&fit=crop',
            # Asian/Stir fry
            'asian': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop',
            'stir': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop',
            # Vegetarian
            'vegetarian': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
            'vegan': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
            # Mexican
            'taco': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop',
            'mexican': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop',
            # Seafood
            'fish': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop',
            'salmon': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop',
            # Desserts
            'cake': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
            'cookie': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
            'dessert': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
            # Breakfast
            'breakfast': 'https://images.unsplash.com/photo-1493770348161-369560ae357d?w=400&h=300&fit=crop',
            'pancake': 'https://images.unsplash.com/photo-1493770348161-369560ae357d?w=400&h=300&fit=crop',
            # Salad
            'salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
            # Soup
            'soup': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop',
            # Pizza
            'pizza': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
            # Burger
            'burger': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop',
            # Steak
            'steak': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop',
            'beef': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop'
        }
        
        # Try to match based on title and ingredients
        for keyword, image_url in fallback_images.items():
            if keyword in all_text:
                return image_url
        
        # Default fallback image for general recipes
        return 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
        
    except Exception as e:
        print(f"Error getting fallback image: {e}")
        # Return a generic food image as ultimate fallback
        return 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'

def test_image_url(image_url, timeout=5):
    """Test if an image URL is accessible"""
    if not image_url:
        return False
    
    try:
        # Quick test to see if the image URL is accessible
        response = requests.head(image_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if content_type.startswith('image/'):
                return True
        return False
    except Exception as e:
        print(f"Error testing image URL {image_url}: {e}")
        return False

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

@app.route('/api/test-image-extraction', methods=['POST'])
def test_image_extraction():
    """Test image extraction from a specific URL for debugging"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        recipe_details = get_recipe_details(url, headers)
        
        if recipe_details:
            return jsonify({
                'success': True,
                'recipe': recipe_details,
                'image_extraction_success': bool(recipe_details.get('image_url'))
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to extract recipe details'}), 500
        
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
        },
        {
            'title': 'Vegetarian Buddha Bowl',
            'ingredients': [
                '1 cup quinoa, cooked',
                '1 sweet potato, cubed and roasted',
                '1 cup chickpeas, drained and rinsed',
                '2 cups kale, chopped',
                '1 avocado, sliced',
                '1/4 cup tahini',
                '2 tablespoons lemon juice',
                '1 tablespoon maple syrup',
                'Salt and pepper to taste'
            ],
            'instructions': [
                'Cook quinoa according to package directions',
                'Preheat oven to 400°F and roast sweet potato cubes for 25-30 minutes',
                'In a bowl, whisk together tahini, lemon juice, maple syrup, salt, and pepper',
                'Assemble bowls with quinoa, roasted sweet potato, chickpeas, and kale',
                'Top with avocado slices and drizzle with tahini dressing',
                'Serve immediately'
            ],
            'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
            'source_url': 'https://example.com/vegetarian-buddha-bowl'
        },
        {
            'title': 'Beef Tacos',
            'ingredients': [
                '1 pound ground beef',
                '1 packet taco seasoning',
                '8 taco shells',
                '1 cup shredded lettuce',
                '1 cup diced tomatoes',
                '1 cup shredded cheese',
                '1/2 cup sour cream',
                '1/4 cup salsa'
            ],
            'instructions': [
                'Brown ground beef in a large skillet over medium heat',
                'Add taco seasoning and water according to package directions',
                'Simmer for 5 minutes until thickened',
                'Warm taco shells in the oven at 350°F for 5 minutes',
                'Fill shells with beef mixture',
                'Top with lettuce, tomatoes, cheese, sour cream, and salsa',
                'Serve immediately'
            ],
            'image_url': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400',
            'source_url': 'https://example.com/beef-tacos'
        }
    ]
    
    # Filter recipes based on query if possible
    query_lower = query.lower()
    if 'chicken' in query_lower:
        return fallback_recipes[:3]  # Return chicken recipes
    elif 'pasta' in query_lower:
        return [fallback_recipes[1]] if max_recipes >= 1 else []
    elif 'vegetarian' in query_lower or 'vegan' in query_lower:
        return [fallback_recipes[3]] if max_recipes >= 1 else []
    elif 'beef' in query_lower or 'taco' in query_lower:
        return [fallback_recipes[4]] if max_recipes >= 1 else []
    elif 'stir' in query_lower or 'asian' in query_lower:
        return [fallback_recipes[2]] if max_recipes >= 1 else []
    else:
        # Return a mix of recipes for general searches
        return fallback_recipes[:min(max_recipes, len(fallback_recipes))]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
