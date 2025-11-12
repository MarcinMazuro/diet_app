"""
BBC Good Food Recipe Scraper - Full Recipe Details
Scrapes complete recipe data including ingredients, instructions, and nutrition
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BBCGoodFoodRecipeScraper:
    """Complete recipe scraper for BBC Good Food"""

    BASE_SEARCH_URL = "https://www.bbcgoodfood.com/search"
    BASE_URL = "https://www.bbcgoodfood.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, start_page: int = 1, end_page: int = 100, delay: float = 1.0):
        """
        Initialize scraper

        Args:
            start_page: Starting page number
            end_page: Ending page number (inclusive)
            delay: Delay between requests in seconds
        """
        self.start_page = start_page
        self.end_page = end_page
        self.delay = delay
        self.recipes = []
        self.failed_urls = []

    def get_recipe_links_from_page(self, page_num: int) -> List[str]:
        """
        Get all recipe links from a search page

        Args:
            page_num: Page number to scrape

        Returns:
            List of recipe URLs
        """
        url = f"{self.BASE_SEARCH_URL}?q=&page={page_num}"
        logger.info(f"Getting recipe links from page {page_num}")

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', class_='card')

            links = []
            for article in articles:
                # Only get recipe articles
                if article.get('data-item-type') == 'recipe':
                    link_elem = article.find('a', class_='link')
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('http'):
                            links.append(href)
                        else:
                            links.append(self.BASE_URL + href)

            logger.info(f"Found {len(links)} recipe links on page {page_num}")
            return links

        except requests.RequestException as e:
            logger.error(f"Error fetching page {page_num}: {e}")
            return []

    def scrape_recipe_details(self, url: str) -> Optional[Dict]:
        """
        Scrape full recipe details from recipe page

        Args:
            url: Recipe URL

        Returns:
            Dictionary with complete recipe data
        """
        logger.info(f"Scraping recipe: {url}")

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            recipe = {'url': url, 'scraped_at': datetime.now().isoformat()}

            # Try to get JSON-LD data first (most reliable)
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                try:
                    ld_data = json.loads(json_ld.string)
                    # Handle list or single object
                    if isinstance(ld_data, list):
                        for item in ld_data:
                            if item.get('@type') == 'Recipe':
                                recipe.update(self._parse_json_ld(item))
                                break
                    elif ld_data.get('@type') == 'Recipe':
                        recipe.update(self._parse_json_ld(ld_data))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON-LD for {url}")

            # Fallback: scrape HTML directly
            if 'name' not in recipe:
                recipe.update(self._scrape_html_recipe(soup))

            return recipe if recipe.get('name') else None

        except requests.RequestException as e:
            logger.error(f"Error scraping recipe {url}: {e}")
            self.failed_urls.append(url)
            return None

    def _parse_json_ld(self, data: Dict) -> Dict:
        """Parse JSON-LD recipe data"""
        recipe = {}

        # Basic info
        recipe['name'] = data.get('name', '')
        recipe['description'] = data.get('description', '')
        recipe['image'] = data.get('image', '')

        # Author
        if 'author' in data:
            author = data['author']
            if isinstance(author, dict):
                recipe['author'] = author.get('name', '')
            else:
                recipe['author'] = str(author)

        # Times
        recipe['prep_time'] = data.get('prepTime', '')
        recipe['cook_time'] = data.get('cookTime', '')
        recipe['total_time'] = data.get('totalTime', '')

        # Servings
        if 'recipeYield' in data:
            yield_val = data['recipeYield']
            if isinstance(yield_val, list):
                recipe['servings'] = yield_val[0] if yield_val else ''
            else:
                recipe['servings'] = str(yield_val)

        # Rating
        if 'aggregateRating' in data:
            rating = data['aggregateRating']
            recipe['rating'] = {
                'value': rating.get('ratingValue', ''),
                'count': rating.get('ratingCount', ''),
                'best': rating.get('bestRating', ''),
                'worst': rating.get('worstRating', '')
            }

        # Ingredients
        if 'recipeIngredient' in data:
            recipe['ingredients'] = data['recipeIngredient']

        # Instructions
        if 'recipeInstructions' in data:
            instructions = data['recipeInstructions']
            if isinstance(instructions, list):
                recipe['instructions'] = []
                for inst in instructions:
                    if isinstance(inst, dict):
                        recipe['instructions'].append(inst.get('text', ''))
                    else:
                        recipe['instructions'].append(str(inst))
            else:
                recipe['instructions'] = [str(instructions)]

        # Nutrition
        if 'nutrition' in data:
            nutrition = data.get('nutrition', {}) or {}
            # keep top-level calories for backward compatibility
            recipe['calories'] = nutrition.get('calories', '')

            recipe['protein'] = nutrition.get('proteinContent', ''),
            recipe['fat'] = nutrition.get('fatContent', ''),
            recipe['saturated_fat']= nutrition.get('saturatedFatContent', ''),
            recipe['fiber']= nutrition.get('fiberContent', ''),
            recipe['sugar']= nutrition.get('sugarContent', ''),
            recipe['sodium']=  nutrition.get('sodiumContent', '')

        # Keywords/Categories
        if 'keywords' in data:
            keywords = data['keywords']
            if isinstance(keywords, str):
                recipe['keywords'] = [k.strip() for k in keywords.split(',')]
            else:
                recipe['keywords'] = keywords

        # Recipe category and cuisine
        recipe['category'] = data.get('recipeCategory', '')
        recipe['cuisine'] = data.get('recipeCuisine', '')

        return recipe

    def _scrape_html_recipe(self, soup: BeautifulSoup) -> Dict:
        """Fallback: scrape recipe from HTML structure"""
        recipe = {}

        # Title
        title = soup.find('h1')
        if title:
            recipe['name'] = title.get_text(strip=True)

        # Description
        desc = soup.find('div', class_='editor-content')
        if desc:
            recipe['description'] = desc.get_text(strip=True)

        # Ingredients
        ingredients_section = soup.find('section', class_='recipe__ingredients')
        if ingredients_section:
            ingredients = []
            for li in ingredients_section.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    ingredients.append(text)
            recipe['ingredients'] = ingredients

        # Method/Instructions
        method_section = soup.find('section', class_='recipe__method-steps')
        if method_section:
            instructions = []
            for li in method_section.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    instructions.append(text)
            recipe['instructions'] = instructions

        return recipe

    def scrape_all(self) -> List[Dict]:
        """
        Scrape all recipes from all pages

        Returns:
            List of all recipe details
        """
        logger.info(f"Starting full recipe scrape from page {self.start_page} to {self.end_page}")

        all_recipe_links = []

        # First, collect all recipe links
        for page_num in range(self.start_page, self.end_page + 1):
            links = self.get_recipe_links_from_page(page_num)
            all_recipe_links.extend(links)
            time.sleep(self.delay)

        logger.info(f"Collected {len(all_recipe_links)} recipe links total")

        # Now scrape each recipe
        for i, url in enumerate(all_recipe_links, 1):
            recipe = self.scrape_recipe_details(url)
            if recipe:
                self.recipes.append(recipe)

            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(all_recipe_links)} recipes scraped")

            time.sleep(self.delay)

        logger.info(f"Scraping complete! Total recipes: {len(self.recipes)}")
        logger.info(f"Failed URLs: {len(self.failed_urls)}")

        return self.recipes

    def save_to_json(self, filename: str = 'data/bbcgoodfood_full_recipes.json'):
        """Save scraped recipes to JSON file without overwriting existing entries."""
        # Load existing data if present
        existing = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing = []

        # Avoid duplicates by URL
        existing_urls = {r.get('url') for r in existing if isinstance(r, dict) and r.get('url')}
        new_items = [r for r in self.recipes if isinstance(r, dict) and r.get('url') not in existing_urls]

        combined = existing + new_items

        # Write combined list back to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(new_items)} new recipes (total {len(combined)}) to {filename}")


    def get_statistics(self) -> Dict:
        """Get statistics about scraped recipes"""
        stats = {
            'total_recipes': len(self.recipes),
            'failed_urls': len(self.failed_urls),
            'recipes_with_nutrition': 0,
            'recipes_with_instructions': 0,
            'recipes_with_ingredients': 0,
            'avg_ingredients': 0,
            'avg_steps': 0
        }

        total_ingredients = 0
        total_steps = 0

        for recipe in self.recipes:
            if recipe.get('nutrition'):
                stats['recipes_with_nutrition'] += 1
            if recipe.get('instructions'):
                stats['recipes_with_instructions'] += 1
                total_steps += len(recipe['instructions'])
            if recipe.get('ingredients'):
                stats['recipes_with_ingredients'] += 1
                total_ingredients += len(recipe['ingredients'])

        if stats['recipes_with_ingredients'] > 0:
            stats['avg_ingredients'] = round(total_ingredients / stats['recipes_with_ingredients'], 1)
        if stats['recipes_with_instructions'] > 0:
            stats['avg_steps'] = round(total_steps / stats['recipes_with_instructions'], 1)

        return stats


def main():
    """Main function to run the scraper"""
    # Test with first 2 pages (about 30-40 recipes)
    scraper = BBCGoodFoodRecipeScraper(start_page=11, end_page=30, delay=0.5)

    # Scrape all recipes
    recipes = scraper.scrape_all()

    # Save to JSON
    scraper.save_to_json('data/bbcgoodfood_full_recipes.json')

    # Print statistics
    stats = scraper.get_statistics()
    logger.info("=" * 60)
    logger.info("SCRAPING STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total recipes scraped: {stats['total_recipes']}")
    logger.info(f"Failed URLs: {stats['failed_urls']}")
    logger.info(f"Recipes with nutrition data: {stats['recipes_with_nutrition']}")
    logger.info(f"Recipes with ingredients: {stats['recipes_with_ingredients']}")
    logger.info(f"Recipes with instructions: {stats['recipes_with_instructions']}")
    logger.info(f"Average ingredients per recipe: {stats['avg_ingredients']}")
    logger.info(f"Average steps per recipe: {stats['avg_steps']}")

    # Show example recipe
    if recipes:
        logger.info("=" * 60)
        logger.info("EXAMPLE RECIPE")
        logger.info("=" * 60)
        example = recipes[0]
        logger.info(f"Name: {example.get('name', 'N/A')}")
        logger.info(f"URL: {example.get('url', 'N/A')}")
        logger.info(f"Ingredients: {len(example.get('ingredients', []))}")
        logger.info(f"Instructions: {len(example.get('instructions', []))}")


if __name__ == '__main__':
    main()

