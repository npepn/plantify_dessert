"""
Plantify Dessert - Flask Application
Main API server for plant-based dessert formulation
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from pathlib import Path

from engine.formulation_engine import FormulationEngine
from engine.ingredient_matcher import IngredientMatcher
from engine.sustainability_calculator import SustainabilityCalculator
from engine.cost_analyzer import CostAnalyzer
from models.ingredient import Ingredient

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize formulation engine
formulation_engine = FormulationEngine()

# Load ingredients database
db_path = Path(__file__).parent / "data" / "ingredients_database.json"
with open(db_path) as f:
    ingredients_data = json.load(f)

ingredients_db = {}
for ing_data in ingredients_data['ingredients']:
    ing = Ingredient.from_dict(ing_data)
    ingredients_db[ing.id] = ing

# Initialize other components
ingredient_matcher = IngredientMatcher(ingredients_db)
sustainability_calc = SustainabilityCalculator()
cost_analyzer = CostAnalyzer()


@app.route('/')
def home():
    """Serve the web interface"""
    return render_template('index.html')


@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Plantify Dessert API',
        'version': '1.0.0',
        'description': 'Plant-based French dessert formulation system',
        'endpoints': {
            'formulate': '/api/formulate',
            'ingredients': '/api/ingredients',
            'desserts': '/api/desserts',
            'compare': '/api/compare',
            'scale': '/api/scale'
        }
    })


@app.route('/api/formulate', methods=['POST'])
def formulate_recipe():
    """
    Generate optimized plant-based dessert recipe
    
    Request body:
    {
        "dessert_type": "eclair",
        "texture": ["crispy", "creamy"],
        "dietary_constraints": ["vegan", "nut_free"],
        "budget_per_unit": 3.50,
        "sustainability_priority": "low_co2",
        "yield_servings": 12
    }
    """
    try:
        request_data = request.get_json()
        
        # Validate required fields
        if 'dessert_type' not in request_data:
            return jsonify({
                'error': 'dessert_type is required'
            }), 400
        
        # Formulate recipe
        result = formulation_engine.formulate(request_data)
        
        return jsonify({
            'success': True,
            'recipe': result
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """
    Get list of all available ingredients
    
    Query parameters:
    - category: Filter by category (optional)
    - role: Filter by functional role (optional)
    - allergen_free: Filter by allergen (optional)
    """
    try:
        category = request.args.get('category')
        role = request.args.get('role')
        allergen_free = request.args.get('allergen_free')
        
        ingredients_list = []
        
        for ingredient in ingredients_db.values():
            # Apply filters
            if category and ingredient.category.value != category:
                continue
            
            if role and role not in [r.value for r in ingredient.functional_roles]:
                continue
            
            if allergen_free and allergen_free.lower() in [a.lower() for a in ingredient.allergens]:
                continue
            
            ingredients_list.append(ingredient.to_dict())
        
        return jsonify({
            'success': True,
            'count': len(ingredients_list),
            'ingredients': ingredients_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ingredients/<ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    """Get details for a specific ingredient"""
    try:
        if ingredient_id not in ingredients_db:
            return jsonify({
                'success': False,
                'error': f'Ingredient {ingredient_id} not found'
            }), 404
        
        ingredient = ingredients_db[ingredient_id]
        
        # Get substitutes
        substitutes = ingredient_matcher.find_substitutes(
            ingredient_id,
            dietary_constraints=['vegan']
        )
        
        result = ingredient.to_dict()
        result['substitute_details'] = [s.to_dict() for s in substitutes]
        
        return jsonify({
            'success': True,
            'ingredient': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/desserts', methods=['GET'])
def get_desserts():
    """Get list of supported dessert types"""
    try:
        desserts = []
        
        for dessert_id, dessert in formulation_engine.dessert_templates.items():
            desserts.append(dessert.to_dict())
        
        return jsonify({
            'success': True,
            'count': len(desserts),
            'desserts': desserts
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/desserts/<dessert_id>', methods=['GET'])
def get_dessert(dessert_id):
    """Get details for a specific dessert type"""
    try:
        if dessert_id not in formulation_engine.dessert_templates:
            return jsonify({
                'success': False,
                'error': f'Dessert {dessert_id} not found'
            }), 404
        
        dessert = formulation_engine.dessert_templates[dessert_id]
        
        return jsonify({
            'success': True,
            'dessert': dessert.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare_recipes():
    """
    Compare plant-based recipe to traditional version
    
    Request body:
    {
        "recipe_id": "eclair_v1_1234",
        "dessert_type": "eclair"
    }
    """
    try:
        request_data = request.get_json()
        dessert_type = request_data.get('dessert_type')
        
        if not dessert_type:
            return jsonify({
                'error': 'dessert_type is required'
            }), 400
        
        # Get traditional baseline
        traditional = sustainability_calc.TRADITIONAL_IMPACTS.get(dessert_type)
        
        if not traditional:
            return jsonify({
                'error': f'No traditional baseline for {dessert_type}'
            }), 404
        
        return jsonify({
            'success': True,
            'traditional': traditional,
            'note': 'Use /api/formulate to get plant-based comparison'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scale', methods=['POST'])
def scale_recipe():
    """
    Scale recipe to different serving size
    
    Request body:
    {
        "recipe": {...},
        "target_servings": 24
    }
    """
    try:
        request_data = request.get_json()
        
        if 'recipe' not in request_data or 'target_servings' not in request_data:
            return jsonify({
                'error': 'recipe and target_servings are required'
            }), 400
        
        # This is a simplified version
        # In production, would use Recipe.scale_recipe() method
        
        return jsonify({
            'success': True,
            'message': 'Recipe scaling functionality',
            'note': 'Use Recipe.scale_recipe() method in Python'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from datetime import datetime
        
        # Check if engine is initialized
        dessert_count = len(formulation_engine.dessert_templates)
        ingredient_count = len(ingredients_db)
        
        return jsonify({
            'status': 'healthy',
            'service': 'Plantify Dessert API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'formulation_engine': 'operational',
                'dessert_templates': dessert_count,
                'ingredient_database': ingredient_count,
                'available_desserts': list(formulation_engine.dessert_templates.keys())
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Plantify Dessert API Server")
    print("=" * 60)
    print("Starting server on http://localhost:5001")
    print("\nAvailable endpoints:")
    print("  GET  /                    - API information")
    print("  POST /api/formulate       - Generate recipe")
    print("  GET  /api/ingredients     - List ingredients")
    print("  GET  /api/desserts        - List desserts")
    print("  GET  /api/health          - Health check")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
