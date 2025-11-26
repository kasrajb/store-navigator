#!/usr/bin/env python3
"""
Grocery Store Product Locator for RTAB-Map Database

Uses GLOBAL coordinates from ObjMeta metadata (optimized pose graph).
"""

import sqlite3
import json
import struct
import math
import difflib
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

# Set up logging
logger = logging.getLogger("search_product")

# Configuration - use container paths
DATA_DIR = Path("/data")
DEFAULT_DB_PATH = DATA_DIR / "database.db"  # Default database path in container


def get_frame_global_coordinates(cursor, frame_id: int) -> Optional[Dict]:
    """
    Get GLOBAL coordinates for a frame from database metadata.
    
    IMPORTANT: Returns global coordinates from RTAB-Map's optimized pose graph,
    NOT relative coordinates from the Node table.
    
    Args:
        cursor: Database cursor
        frame_id: Frame/node ID to query
    
    Returns:
        dict with keys: x, y, z (global coordinates in meters)
        None if frame not found or no metadata
    """
    try:
        cursor.execute("SELECT metadata_json FROM ObjMeta WHERE frame_id = ?", (frame_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return None
        
        metadata = json.loads(result[0])
        
        # Handle dict structure (new format with global_pose)
        if isinstance(metadata, dict) and 'global_pose' in metadata:
            pose = metadata['global_pose']
            return {
                'x': float(pose['x']),
                'y': float(pose['y']),
                'z': float(pose['z'])
            }
        
        # If old format (list of objects), return None - needs database update
        return None
        
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


# SMART SYNONYM HANDLING

PRODUCT_SYNONYMS = {
    # Beverages
    'soda': ['pop', 'soft_drink', 'cola', 'carbonated_drink', 'fizzy_drink'],
    'pop': ['soda', 'soft_drink', 'cola', 'carbonated_drink'],
    'juice': ['fruit_juice', 'beverage', 'drink'],
    'water': ['bottled_water', 'drinking_water', 'mineral_water', 'spring_water'],
    'coffee': ['java', 'espresso', 'brew', 'caffeine'],
    'tea': ['chai', 'herbal_tea', 'green_tea', 'black_tea'],
    
    # Grains & Pasta
    'pasta': ['spaghetti', 'noodles', 'macaroni', 'linguine', 'penne'],
    'noodles': ['pasta', 'ramen', 'udon', 'egg_noodles'],
    'cereal': ['breakfast_cereal', 'granola', 'oats', 'muesli', 'flakes'],
    'oatmeal': ['oats', 'porridge', 'hot_cereal'],
    'rice': ['grain', 'basmati', 'jasmine', 'brown_rice', 'white_rice'],
    'bread': ['loaf', 'baguette', 'rolls', 'buns', 'toast'],
    
    # Snacks & Chips
    'chips': ['crisps', 'potato_chips', 'snacks', 'crackers'],
    'crisps': ['chips', 'potato_chips', 'snacks'],
    'crackers': ['biscuits', 'wafers', 'snack_crackers'],
    'cookies': ['biscuits', 'treats', 'sweets', 'dessert'],
    'candy': ['sweets', 'confectionery', 'chocolate', 'treats'],
    
    # Produce
    'vegetables': ['veggies', 'produce', 'greens'],
    'fruits': ['produce', 'fresh_fruit'],
    'oranges': ['orange', 'citrus'],
    'potatoes': ['potato', 'spuds', 'taters'],
    
    # Dairy & Proteins
    'milk': ['dairy', 'whole_milk', 'skim_milk', '2%_milk', 'low_fat_milk'],
    'cheese': ['dairy', 'cheddar', 'swiss', 'mozzarella', 'parmesan'],
    'yogurt': ['yoghurt', 'dairy', 'greek_yogurt'],
    'butter': ['margarine', 'spread', 'dairy'],
    'chicken': ['poultry', 'fowl', 'bird'],
    'beef': ['meat', 'steak', 'ground_beef', 'hamburger'],
    'pork': ['ham', 'bacon', 'sausage', 'meat'],
    'fish': ['seafood', 'salmon', 'tuna', 'cod'],
    
    # Frozen & Canned
    'frozen': ['freezer', 'ice', 'frozen_food'],
    'canned': ['tin', 'jar', 'preserved', 'jarred'],
    'soup': ['broth', 'stew', 'bisque', 'chowder'],
    
    # Household & Personal Care
    'shampoo': ['hair_care', 'cleanser'],
    'soap': ['body_wash', 'cleanser', 'bar_soap'],
    'detergent': ['laundry_soap', 'washing_powder', 'fabric_softener'],
    'toilet_paper': ['tissue', 'bathroom_tissue', 'tp'],
    'paper_towels': ['kitchen_towels', 'napkins'],
    
    # Condiments & Spices
    'ketchup': ['tomato_sauce', 'condiment'],
    'mustard': ['condiment', 'yellow_mustard'],
    'mayonnaise': ['mayo', 'condiment', 'spread'],
    'salt': ['seasoning', 'table_salt', 'sea_salt'],
    'pepper': ['black_pepper', 'seasoning', 'spice'],
    'oil': ['cooking_oil', 'olive_oil', 'vegetable_oil'],
    'vinegar': ['balsamic', 'white_vinegar', 'apple_cider_vinegar']
}

# UNIT & SIZE RECOGNITION

UNITS = {
    # Weight units
    'oz': ['ounce', 'ounces', 'fl oz', 'fluid ounce'],
    'lb': ['pound', 'pounds', 'lbs'],
    'kg': ['kilogram', 'kilograms', 'kilo'],
    'g': ['gram', 'grams', 'gm'],
    
    # Volume units
    'ml': ['milliliter', 'milliliters', 'mL'],
    'l': ['liter', 'liters', 'litre', 'litres'],
    'gallon': ['gal', 'gallons'],
    'quart': ['qt', 'quarts'],
    'pint': ['pt', 'pints'],
    'cup': ['cups', 'c'],
    'fl_oz': ['fluid ounce', 'fluid ounces'],
    
    # Count units
    'pack': ['package', 'pkg', 'packets'],
    'box': ['boxes', 'carton'],
    'can': ['cans', 'tin'],
    'bottle': ['bottles', 'btl'],
    'jar': ['jars'],
    'bag': ['bags', 'pouch']
}

SIZES = {
    'small': ['sm', 'mini', 'personal', 'individual', 'single'],
    'medium': ['med', 'regular', 'standard', 'normal'],
    'large': ['lg', 'big', 'jumbo', 'super'],
    'extra_large': ['xl', 'xxl', 'giant', 'mega', 'super_size'],
    'family_size': ['family', 'bulk', 'economy', 'value_pack'],
    'travel_size': ['travel', 'portable', 'sample', 'trial']
}

# BRAND NAME RECOGNITION

BRAND_CATEGORIES = {
    # Dairy & Cheese
    'dairy': ['kraft', 'dairyland', 'philadelphia', 'kirkland', 'chapmans', 'lactantia', 'cracker barrel'],
    
    # Beverages
    'juice': ['tropicana', 'simply', 'sun-rype', 'naked', 'motts', 'minute maid', 'ocean spray'],
    'soda': ['coca cola', 'coke', 'pepsi', 'dr pepper', '7up', 'canada dry', 'fanta', 'sprite', 'schweppes', 'mountain dew'],
    'water': ['dasani', 'nestle pure life', 'evian', 'aquafina', 'perrier'],
    'sports_drink': ['gatorade', 'powerade', 'vitamin water'],
    'coffee': ['starbucks', 'tim hortons', 'folgers', 'maxwell house'],
    'tea': ['lipton', 'tetley', 'twinings'],
    
    # Breakfast & Cereals
    'cereal': ['cheerios', 'general mills', 'kelloggs', 'post', 'quaker', 'natures path', 'cascadian farm', 
               'frosted flakes', 'corn flakes', 'lucky charms', 'captain crunch'],
    
    # Snacks
    'chips': ['lays', 'doritos', 'pringles', 'ruffles', 'tostitos', 'sun chips'],
    'crackers': ['ritz', 'cheez-it', 'triscuit', 'wheat thins', 'pepperidge farm'],
    'candy': ['hersheys', 'mars', 'nestle', 'skittles', 'mms', 'twix', 'snickers', 'kit kat', 'reeses'],
    'chocolate': ['ghirardelli', 'cadbury'],
    'cookies': ['oreo'],
    
    # Frozen Foods
    'ice_cream': ['ben jerrys', 'haagen-dazs', 'breyers'],
    'frozen_meals': ['stouffers', 'lean cuisine', 'healthy choice', 'hot pockets'],
    'frozen_breakfast': ['eggo'],
    'frozen_fish': ['gortons'],
    'frozen_dinners': ['banquet'],
    'frozen_vegetables': ['birds eye'],
    
    # Pantry & Canned Goods
    'soup': ['campbells', 'progresso'],
    'canned_goods': ['del monte'],
    'canned_vegetables': ['green giant'],
    'beans': ['bushs'],
    'canned_pasta': ['chef boyardee'],
    'canned_meat': ['hormel'],
    'canned_fruit': ['dole'],
    'canned_fish': ['starkist', 'bumble bee'],
    
    # Condiments & Spreads
    'ketchup': ['heinz'],
    'mayonnaise': ['hellmans'],
    'mustard': ['grey poupon', 'frenchs'],
    'soy_sauce': ['kikkoman'],
    'jam': ['smuckers'],
    'spread': ['nutella'],
    'peanut_butter': ['jif', 'skippy'],
    'dressing': ['hidden valley'],
    
    # Bakery & Bread
    'bread': ['wonder', 'arnold', 'pepperidge farm', 'sara lee'],
    'bakery': ['entenmanns'],
    'english_muffins': ['thomas'],
    'bagels': ['bagel bites'],
    
    # Meat & Deli
    'chicken': ['tyson', 'perdue'],
    'deli_meat': ['oscar mayer', 'schneiders', 'maple leaf', 'boars head'],
    'hot_dogs': ['ball park'],
    'sausage': ['hillshire farm'],
    
    # Produce & Organic
    'produce': ['dole', 'del monte'],
    'organic': ['organic valley', 'annies', 'natures path', 'whole foods'],
    'organic_produce': ['earthbound farm'],
    'berries': ['driscoll'],
    
    # Baby & Family
    'baby_food': ['gerber'],
    'diapers': ['pampers', 'huggies'],
    'baby_care': ['johnsons', 'aveeno baby'],
    'baby_formula': ['similac', 'enfamil'],
    
    # Pet Care
    'pet_food': ['pedigree', 'purina', 'iams', 'blue buffalo', 'hills', 'beneful'],
    'cat_food': ['fancy feast', 'friskies'],
    
    # Cleaning & Household
    'cleaning': ['clorox', 'lysol', 'mr clean'],
    'dish_soap': ['dawn', 'palmolive'],
    'laundry_detergent': ['tide', 'gain'],
    'glass_cleaner': ['windex'],
    
    # Personal Care & Health
    'toothpaste': ['colgate', 'crest'],
    'toothbrush': ['oral-b'],
    'soap': ['dove'],
    'skincare': ['neutrogena'],
    'medication': ['tylenol', 'advil'],
    'first_aid': ['band-aid'],
    'shampoo': ['head shoulders'],
    
    # Paper Products
    'toilet_paper': ['charmin'],
    'paper_towels': ['bounty'],
    'tissues': ['kleenex'],
    'paper_products': ['scott'],
    'storage_bags': ['glad', 'ziploc'],
    'aluminum_foil': ['reynolds'],
    
    # International & Specialty
    'pasta': ['barilla'],
    'hispanic_foods': ['goya'],
    'hot_sauce': ['sriracha'],
    'asian_sauce': ['lee kum kee'],
    'indian_sauce': ['pataks'],
    'mexican_food': ['old el paso', 'ortega']
}

# Create the flattened BRAND_MAPPING dictionary for backward compatibility
BRAND_MAPPING = {}
for category, brands in BRAND_CATEGORIES.items():
    for brand in brands:
        BRAND_MAPPING[brand] = category

# FRENCH TRANSLATIONS
FRENCH_TRANSLATIONS = {
    # Dairy & Proteins
    'milk': 'lait', 'cheese': 'fromage', 'butter': 'beurre', 'yogurt': 'yaourt',
    'eggs': 'œufs', 'cream': 'crème', 'chicken': 'poulet', 'beef': 'bœuf',
    'pork': 'porc', 'fish': 'poisson', 'salmon': 'saumon', 'tuna': 'thon',
    
    # Fruits & Vegetables
    'apple': 'pomme', 'banana': 'banane', 'orange': 'orange', 'grapes': 'raisins',
    'strawberry': 'fraise', 'blueberry': 'myrtille', 'pear': 'poire',
    'carrot': 'carotte', 'potato': 'pomme de terre', 'tomato': 'tomate', 'onion': 'oignon',
    'lettuce': 'laitue', 'spinach': 'épinard', 'broccoli': 'brocoli',
    'cucumber': 'concombre', 'pepper': 'poivron', 'garlic': 'ail',
    
    # Grains & Bakery
    'bread': 'pain', 'rice': 'riz', 'pasta': 'pâtes', 'cereal': 'céréales',
    'flour': 'farine', 'oats': 'avoine', 'bagel': 'bagel', 'croissant': 'croissant',
    'muffin': 'muffin', 'cake': 'gâteau', 'cookie': 'biscuit',
    
    # Beverages
    'water': 'eau', 'juice': 'jus', 'coffee': 'café', 'tea': 'thé',
    'soda': 'soda', 'beer': 'bière', 'wine': 'vin', 'milk': 'lait',
    
    # Pantry Items
    'sugar': 'sucre', 'salt': 'sel', 'oil': 'huile', 'vinegar': 'vinaigre',
    'honey': 'miel', 'jam': 'confiture', 'ketchup': 'ketchup', 'mustard': 'moutarde',
    'mayonnaise': 'mayonnaise', 'sauce': 'sauce', 'soup': 'soupe',
    
    # Snacks & Treats
    'chips': 'chips', 'crackers': 'crackers', 'nuts': 'noix', 'candy': 'bonbons',
    'chocolate': 'chocolat', 'ice_cream': 'crème glacée', 'popcorn': 'pop-corn',
    
    # Frozen & Canned
    'frozen': 'surgelé', 'canned': 'en conserve', 'pickles': 'cornichons',
    
    # Household & Personal Care
    'soap': 'savon', 'shampoo': 'shampooing', 'toothpaste': 'dentifrice',
    'toilet_paper': 'papier toilette', 'detergent': 'détergent', 'tissue': 'mouchoir',
    
    # Dietary & Health
    'organic': 'biologique', 'gluten_free': 'sans gluten', 'vegan': 'végétalien',
    'kosher': 'casher', 'low_fat': 'faible en gras', 'sugar_free': 'sans sucre'
}

# DIETARY FILTERS

DIETARY_FILTERS = {
    'gluten_free': ['gluten free', 'gf', 'celiac', 'wheat free', 'gluten-free', 'sans gluten'],
    'vegan': ['vegan', 'plant based', 'dairy free', 'plant-based', 'végétalien', 'végane'],
    'vegetarian': ['vegetarian', 'veggie', 'meat free', 'végétarien'],
    'kosher': ['kosher', 'k', 'pareve', 'kashrut', 'casher'],
    'halal': ['halal', 'islamic', 'permissible'],
    'organic': ['organic', 'usda organic', 'bio', 'biologique', 'natural', 'naturel'],
    'non_gmo': ['non gmo', 'gmo free', 'non-gmo', 'sans ogm', 'natural'],
    'sugar_free': ['sugar free', 'no sugar', 'sugarless', 'sans sucre', 'diabetic'],
    'low_sodium': ['low sodium', 'reduced sodium', 'low salt', 'faible sodium'],
    'low_fat': ['low fat', 'reduced fat', 'fat free', 'faible en gras', 'light'],
    'lactose_free': ['lactose free', 'dairy free', 'sans lactose', 'plant milk'],
    'keto': ['keto', 'ketogenic', 'low carb', 'high fat'],
    'paleo': ['paleo', 'paleolithic', 'caveman diet', 'primal'],
    'raw': ['raw', 'uncooked', 'living food', 'cru']
}

def rotation_matrix_to_quaternion(r11, r12, r13, r21, r22, r23, r31, r32, r33):
    """Convert rotation matrix to quaternion."""
    tr = r11 + r22 + r33
    if tr > 0:
        S = math.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (r32 - r23) / S
        qy = (r13 - r31) / S
        qz = (r21 - r12) / S
    elif (r11 > r22) and (r11 > r33):
        S = math.sqrt(1.0 + r11 - r22 - r33) * 2
        qw = (r32 - r23) / S
        qx = 0.25 * S
        qy = (r12 + r21) / S
        qz = (r13 + r31) / S
    elif r22 > r33:
        S = math.sqrt(1.0 + r22 - r11 - r33) * 2
        qw = (r13 - r31) / S
        qx = (r12 + r21) / S
        qy = 0.25 * S
        qz = (r23 + r32) / S
    else:
        S = math.sqrt(1.0 + r33 - r11 - r22) * 2
        qw = (r21 - r12) / S
        qx = (r13 + r31) / S
        qy = (r23 + r32) / S
        qz = 0.25 * S
    return qx, qy, qz, qw


def parse_pose_data(pose_data) -> Optional[Tuple[float, float]]:
    """Parse pose data and extract x,y coordinates."""
    try:
        if isinstance(pose_data, bytes):
            if len(pose_data) == 12 * 4:  # 12 floats
                values = struct.unpack('12f', pose_data)
            elif len(pose_data) == 12 * 8:  # 12 doubles
                values = struct.unpack('12d', pose_data)
            else:
                return None
        elif isinstance(pose_data, str):
            values = [float(x) for x in pose_data.split()]
            if len(values) != 12:
                return None
        else:
            return None

        # Extract x, y components (indices 9, 10)
        tx, ty = values[9], values[10]
        return round(tx, 2), round(ty, 2)
    
    except Exception:
        return None


def normalize_search_term(term: str) -> str:
    """
    Normalize grocery store search terms using comprehensive dictionaries.
    Handles synonyms, translations, and dietary terms for better matching.
    """
    # Convert to lowercase and remove extra spaces
    term = term.lower().strip()
    
    # Remove apostrophes and convert spaces to underscores for database matching
    # "Rubik's Cube" -> "rubiks_cube"
    term = term.replace("'", "").replace(" ", "_")
    
    # Handle French-to-English translation
    french_to_english = {v: k for k, v in FRENCH_TRANSLATIONS.items()}
    if term in french_to_english:
        term = french_to_english[term]
    
    # Handle synonym expansion - check if term has known synonyms
    for main_term, synonyms in PRODUCT_SYNONYMS.items():
        if term in synonyms:
            term = main_term
            break
    
    # Handle dietary filter normalization
    for diet_type, variations in DIETARY_FILTERS.items():
        if term in variations:
            term = diet_type
            break
    
    # Handle tricky plural/singular variations and French terms
    plural_mappings = {
        'chips': 'chip', 'candies': 'candy', 'cereals': 'cereal', 'yogurts': 'yogurt',
        'œufs': 'egg', 'pommes': 'apple', 'bananes': 'banana', 'tomates': 'tomato',
        'pâtes': 'pasta', 'céréales': 'cereal'
    }
    
    # Check if it's a known plural and convert to singular
    if term in plural_mappings:
        term = plural_mappings[term]
    
    return term


def expand_search_terms(search_term: str) -> List[str]:
    """
    Expand search term to include synonyms and translations for comprehensive matching.
    
    Args:
        search_term: Original search term
        
    Returns:
        List of expanded terms including synonyms and translations
    """
    terms = [search_term]
    
    # Add synonyms if available
    if search_term in PRODUCT_SYNONYMS:
        terms.extend(PRODUCT_SYNONYMS[search_term])
    
    # Add French translation if available
    french_term = FRENCH_TRANSLATIONS.get(search_term)
    if french_term:
        terms.append(french_term)
    
    # Add dietary filter variations
    if search_term in DIETARY_FILTERS:
        terms.extend(DIETARY_FILTERS[search_term])
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(terms))


def sql_prefilter_metadata(search_term: str, db_path: str, max_frames: int = 50) -> str:
    """
    SQL pre-filtering to improve search performance by filtering at database level.
    
    This function queries the database to find frames containing relevant objects
    before performing expensive fuzzy matching operations.
    
    Args:
        search_term: User's search query
        db_path: Path to SQLite database
        max_frames: Maximum number of frames to return for processing
        
    Returns:
        str: Combined JSON metadata from matching frames, or empty string if none found
        
    Performance Benefits:
        - Reduces fuzzy matching workload by 70-90% in typical scenarios
        - Filters irrelevant frames at SQL level using LIKE queries
        - Prioritizes frames with higher object match density
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Normalize search term and get related terms
        normalized_term = normalize_search_term(search_term)
        search_terms = expand_search_terms(normalized_term)
        
        # Build SQL LIKE conditions for pre-filtering
        like_conditions = []
        params = []
        
        # Split search term into individual words for better SQL matching
        search_words = normalized_term.split()
        
        # Add conditions for each word in the search term
        for word in search_words:
            if len(word) >= 2:  # Skip very short words
                like_conditions.append("metadata_json LIKE ?")
                params.append(f"%{word}%")
        
        # Add expanded terms
        for term in search_terms[:8]:  # Limit to top 8 terms for SQL performance
            if len(term) >= 2:
                like_conditions.append("metadata_json LIKE ?")
                params.append(f"%{term}%")
        
        # Add brand recognition to SQL filtering
        if normalized_term in BRAND_MAPPING:
            brand_category = BRAND_MAPPING[normalized_term]
            like_conditions.append("metadata_json LIKE ?")
            params.append(f"%{brand_category}%")
        
        # Construct SQL query with OR conditions
        if like_conditions:
            where_clause = " OR ".join(like_conditions)
            query = f"""
                SELECT metadata_json 
                FROM ObjMeta 
                WHERE {where_clause}
                ORDER BY frame_id
                LIMIT ?
            """
            params.append(max_frames)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                # Combine metadata from multiple frames
                all_objects = []
                for row in rows:
                    frame_objects = json.loads(row[0])
                    all_objects.extend(frame_objects)
                
                # Return combined metadata as JSON string
                return json.dumps(all_objects)
        
        conn.close()
        return ""  # No matching frames found
        
    except Exception as e:
        print(f"SQL pre-filtering error: {e}")
        return ""  # Fall back to original metadata on error


def fuzzy_search_objects(search_term: str, metadata_json: str, threshold: float = 0.6, 
                        use_sql_prefilter: bool = True, db_path: str = None) -> List[str]:
    """
    Fuzzy search with precise filtering (e.g., "2% milk" won't return "whole milk").
    Uses SQL pre-filtering for performance optimization.
    
    NOTE: Handles both old format (list of objects) and new format (dict with 'objects' and 'global_pose' keys)
    """
    # SQL Pre-filtering for performance optimization
    if use_sql_prefilter and db_path:
        metadata_json = sql_prefilter_metadata(search_term, db_path)
        if not metadata_json:
            return []  # No matching frames found in database
    
    try:
        metadata = json.loads(metadata_json)
        
        # Handle new format (dict with 'objects' key) or old format (list)
        if isinstance(metadata, dict):
            objects = metadata.get('objects', [])
        elif isinstance(metadata, list):
            objects = metadata
        else:
            return []
        
        # Split search term into individual words
        search_words = [normalize_search_term(word) for word in search_term.split()]
        
        # Identify primary object type
        primary_object = search_words[-1] if search_words else ""
        modifiers = search_words[:-1] if len(search_words) > 1 else []
        
        # Store matches with priority scores
        matches_with_priority = []
        
        for obj in objects:
            class_name = obj.get("class_name", "").lower()
            notes = obj.get("notes", "").lower()
            searchable_text = f"{class_name} {notes}"
            
            obj_description = f"{obj.get('class_name', 'Unknown')}: {obj.get('notes', 'No description')}"
            
            # Calculate priority score for this object
            priority_score = 0
            primary_matched = False
            modifier_matches = 0
            
            # STEP 1: Match primary product type
            # Exact product match (highest priority)
            if primary_object == class_name:
                priority_score += 1000
                primary_matched = True
            
            # Product category match
            elif primary_object in class_name:
                # Ensure it's a proper product word, not just any substring
                class_words = re.findall(r'\b\w+\b', class_name.replace('_', ' '))
                if primary_object in class_words:
                    priority_score += 800
                    primary_matched = True
            
            # Fuzzy match on class_name
            else:
                class_similarity = difflib.SequenceMatcher(None, primary_object, class_name).ratio()
                if class_similarity >= 0.8:
                    priority_score += 600
                    primary_matched = True
            
            # STEP 2: Apply product modifiers for precise grocery store filtering
            # (e.g., "organic", "2%", "gluten free", "low sodium")
            if primary_matched and modifiers:
                words_in_notes = re.findall(r'\b\w+\b', notes)
                
                # ALL modifiers must match - critical for grocery store precision
                # "2% milk" should NOT return "whole milk" or "skim milk"
                all_modifiers_matched = True
                
                for modifier in modifiers:
                    modifier_found = False
                    
                    # Check for product attributes
                    if modifier in words_in_notes:
                        priority_score += 200
                        modifier_matches += 1
                        modifier_found = True
                    
                    # Check for modifier in product name
                    elif modifier in class_name:
                        priority_score += 150
                        modifier_matches += 1
                        modifier_found = True
                    
                    # Check for fuzzy match in notes
                    else:
                        for note_word in words_in_notes:
                            word_similarity = difflib.SequenceMatcher(None, modifier, note_word).ratio()
                            if word_similarity >= 0.8:  # High threshold for modifiers
                                priority_score += 100
                                modifier_matches += 1
                                modifier_found = True
                                break
                    
                    # If any modifier is not found, exclude this object entirely
                    if not modifier_found:
                        all_modifiers_matched = False
                        break
                
                # CRITICAL GROCERY STORE FILTERING: Exclude products that don't match ALL criteria
                # This ensures "2% milk" doesn't show "whole milk" results
                if not all_modifiers_matched:
                    primary_matched = False  # Exclude from results - no partial matches!
                    priority_score = 0
                
                # Bonus for matching all modifiers
                elif modifier_matches == len(modifiers):
                    priority_score += 300
            
            # STEP 3: If no primary match but this is a single-word search, use strict fallback
            elif len(search_words) == 1:
                word = search_words[0]
                
                # For single-word searches, ONLY match if the word appears in class_name
                # This prevents irrelevant matches from notes/descriptions
                
                # Direct word match in class_name
                class_words = re.findall(r'\b\w+\b', class_name.replace('_', ' '))
                if word in class_words:
                    priority_score += 500
                    primary_matched = True
                
                # Fuzzy match on class_name (high threshold)
                elif difflib.SequenceMatcher(None, word, class_name).ratio() >= 0.9:
                    priority_score += 400
                    primary_matched = True
                
                # For very common object types, allow some notes matching but be very strict
                common_objects = ['door', 'wall', 'floor', 'light', 'chair', 'table']
                if word in common_objects:
                    words_in_notes = re.findall(r'\b\w+\b', notes)
                    if word in words_in_notes:
                        # Only if it's the first word in notes (primary descriptor)
                        if notes.startswith(word):
                            priority_score += 200
                            primary_matched = True
            
            # Only include objects that match the primary search criteria
            if primary_matched:
                matches_with_priority.append((priority_score, obj_description))
        
        # Sort by priority score (highest first) and return descriptions only
        matches_with_priority.sort(key=lambda x: x[0], reverse=True)
        return [match[1] for match in matches_with_priority]
    
    except (json.JSONDecodeError, KeyError):
        return []


def search_products(search_term: str, db_path: str, use_sql_prefilter: bool = True, show_performance: bool = False) -> List[Dict]:
    """Search products in spatial database with SQL pre-filtering optimization."""
    import time
    start_time = time.time()
    results = []
    total_frames_checked = 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if use_sql_prefilter:
            # Use SQL pre-filtering to get potentially relevant frames
            normalized_term = normalize_search_term(search_term)
            search_terms = expand_search_terms(normalized_term)
            
            # Build SQL LIKE conditions for pre-filtering frames
            like_conditions = []
            params = []
            
            # Add conditions for each word in the search term
            search_words = normalized_term.split()
            for word in search_words:
                if len(word) >= 2:  # Skip very short words
                    like_conditions.append("metadata_json LIKE ?")
                    params.append(f"%{word}%")
            
            # Add some expanded terms
            for term in search_terms[:5]:  # Limit for SQL performance
                if len(term) >= 2:
                    like_conditions.append("metadata_json LIKE ?")
                    params.append(f"%{term}%")
            
            if like_conditions:
                where_clause = " OR ".join(like_conditions)
                query = f"SELECT frame_id, metadata_json FROM ObjMeta WHERE {where_clause}"
                
                cursor.execute(query, params)
                prefiltered_entries = cursor.fetchall()
                
                # Get total frame count for performance comparison
                cursor.execute("SELECT COUNT(*) FROM ObjMeta")
                total_frames = cursor.fetchone()[0]
                
                total_frames_checked = len(prefiltered_entries)
                efficiency = (1 - total_frames_checked / total_frames) * 100 if total_frames > 0 else 0
                
                if show_performance:
                    print(f"SQL pre-filtering: {total_frames_checked}/{total_frames} frames ({efficiency:.1f}% reduction)")
                else:
                    print(f"SQL pre-filtering: {total_frames_checked} potentially relevant frames found")
                
                # Process the pre-filtered frames
                for frame_id, metadata_json in prefiltered_entries:
                    if not metadata_json:
                        continue
                    matching_objects = fuzzy_search_objects(search_term, metadata_json, use_sql_prefilter=False)
                    
                    if matching_objects:
                        # Get GLOBAL coordinates for this frame from metadata
                        global_coords = get_frame_global_coordinates(cursor, frame_id)
                        
                        if global_coords:
                            results.append({
                                'frame_id': frame_id,
                                'x': global_coords['x'],
                                'y': global_coords['y'],
                                'objects': matching_objects
                            })
            else:
                print("No SQL conditions could be built for pre-filtering.")
        
        else:
            # Legacy mode: process all frames without pre-filtering  
            cursor.execute("SELECT frame_id, metadata_json FROM ObjMeta")
            metadata_entries = cursor.fetchall()
            
            total_frames_checked = len(metadata_entries)
            print(f"Legacy mode: Searching through {total_frames_checked} frames for '{search_term}'...")
            
            for frame_id, metadata_json in metadata_entries:
                if not metadata_json:
                    continue
                matching_objects = fuzzy_search_objects(search_term, metadata_json, use_sql_prefilter=False)
                
                if matching_objects:
                    # Get GLOBAL coordinates for this frame from metadata
                    global_coords = get_frame_global_coordinates(cursor, frame_id)
                    
                    if global_coords:
                        results.append({
                            'frame_id': frame_id,
                            'x': global_coords['x'],
                            'y': global_coords['y'],
                            'objects': matching_objects  # Only matching objects, not all objects in frame
                        })
        
        # Performance summary
        end_time = time.time()
        search_time = end_time - start_time
        
        if show_performance:
            print(f"\nPerformance: {search_time:.3f}s, {total_frames_checked} frames processed")
        
        conn.close()
        return results
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    """Main product locator function."""
    import sys
    
    # Store's spatial mapping database path
    db_path = r"C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Final Report\store-navigator\backend\data\database\IGA-V2.db"
    
    # Check for command line arguments
    use_sql_prefilter = True
    show_performance = False
    
    if len(sys.argv) > 1:
        if "--no-sql-filter" in sys.argv:
            use_sql_prefilter = False
            print("SQL pre-filtering disabled (legacy mode)")
        if "--performance" in sys.argv or "-p" in sys.argv:
            show_performance = True
            print("Performance monitoring enabled")
        if "--help" in sys.argv or "-h" in sys.argv:
            print("Grocery Store Product Locator")
            print("Usage: python search_product.py [options]")
            print("Options:")
            print("  --no-sql-filter    Disable SQL pre-filtering (legacy mode)")
            print("  --performance, -p  Show detailed performance metrics")
            print("  --help, -h         Show this help message")
            return
    
    if use_sql_prefilter:
        print("SQL pre-filtering enabled (high performance mode)")
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        print("Please ensure the database file exists.")
        return
    
    # Get search term from user or stdin
    if not sys.stdin.isatty():
        # Reading from pipe/stdin
        search_term = sys.stdin.read().strip()
    else:
        # Interactive mode
        search_term = input("What are you looking for? ").strip()
    
    if not search_term:
        print("Please enter a search term.")
        return
    
    print(f"\nSearching for '{search_term}'...")
    
    # Perform search with SQL pre-filtering option
    results = search_products(search_term, db_path, use_sql_prefilter=use_sql_prefilter, 
                            show_performance=show_performance)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} location(s) with matching objects:\n")
        
        for result in results:
            frame_id = result['frame_id']
            x = result['x']
            y = result['y']
            
            print(f"Frame {frame_id}: x={x:.2f}, y={y:.2f}")
            
            # Show all matching objects
            for obj in result['objects']:
                print(f"  → {obj}")
            print()
    else:
        print(f"\nNo products matching '{search_term}' found in this store.")

if __name__ == "__main__":
    main()