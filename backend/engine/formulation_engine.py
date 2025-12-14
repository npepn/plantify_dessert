"""
Formulation Engine
Core logic for generating optimized plant-based dessert recipes.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from models.ingredient import (
    Ingredient, FunctionalRole, IngredientCategory
)
from models.dessert import Dessert, create_eclair_template, create_creme_brulee_template
from models.recipe import (
    Recipe, RecipeIngredient, RecipeStep, Unit,
    SustainabilityScore, CostAnalysis, NutritionalInfo,
    PredictiveAnalysis
)
from engine.ingredient_matcher import IngredientMatcher
from engine.sustainability_calculator import SustainabilityCalculator
from engine.cost_analyzer import CostAnalyzer
from engine.predictive_simulator import PredictiveSimulator


class FormulationEngine:
    """
    Main engine for formulating plant-based dessert recipes
    """
    
    def __init__(self, ingredients_db_path: Optional[str] = None):
        """
        Initialize the formulation engine
        
        Args:
            ingredients_db_path: Path to ingredients database JSON
        """
        if ingredients_db_path is None:
            # Default path relative to this file
            base_path = Path(__file__).parent.parent
            ingredients_db_path = base_path / "data" / "ingredients_database.json"
        
        # Load ingredients database
        self.ingredients = self._load_ingredients(ingredients_db_path)
        
        # Initialize sub-engines
        self.ingredient_matcher = IngredientMatcher(self.ingredients)
        self.sustainability_calc = SustainabilityCalculator()
        self.cost_analyzer = CostAnalyzer()
        self.simulator = PredictiveSimulator()
        
        # Load dessert templates
        self.dessert_templates = {
            'eclair': create_eclair_template(),
            'creme_brulee': create_creme_brulee_template()
        }
    
    def _load_ingredients(self, db_path: Path) -> Dict[str, Ingredient]:
        """Load ingredients from JSON database"""
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        ingredients = {}
        for ing_data in data['ingredients']:
            ingredient = Ingredient.from_dict(ing_data)
            ingredients[ingredient.id] = ingredient
        
        return ingredients
    
    def formulate(self, request: Dict) -> Dict:
        """
        Main formulation method
        
        Args:
            request: Dictionary with formulation parameters:
                - dessert_type: str (e.g., 'eclair', 'creme_brulee')
                - texture: str or List[str] (desired textures)
                - dietary_constraints: List[str] (e.g., ['vegan', 'nut_free'])
                - budget_per_unit: float (max cost per serving in EUR)
                - sustainability_priority: str ('low_co2', 'low_water', 'balanced')
                - yield_servings: int (optional, default from template)
        
        Returns:
            Dictionary with complete recipe and analysis
        """
        # Validate request
        dessert_type = request.get('dessert_type')
        if dessert_type not in self.dessert_templates:
            raise ValueError(
                f"Unsupported dessert type: {dessert_type}. "
                f"Available: {list(self.dessert_templates.keys())}"
            )
        
        # Get dessert template
        dessert = self.dessert_templates[dessert_type]
        
        # Extract parameters
        dietary_constraints = request.get('dietary_constraints', ['vegan'])
        budget_per_unit = request.get('budget_per_unit', 5.0)
        sustainability_priority = request.get(
            'sustainability_priority', 'balanced'
        )
        yield_servings = request.get('yield_servings', dessert.typical_yield)
        
        # Step 1: Match ingredients for each component
        recipe_ingredients = []
        component_formulations = []
        
        for component in dessert.components:
            formulation = self._formulate_component(
                component,
                dietary_constraints,
                sustainability_priority
            )
            component_formulations.append(formulation)
            recipe_ingredients.extend(formulation['ingredients'])
        
        # Step 2: Calculate sustainability metrics
        sustainability = self.sustainability_calc.calculate_recipe_impact(
            recipe_ingredients,
            self.ingredients,
            yield_servings
        )
        
        # Step 3: Calculate costs
        cost_analysis = self.cost_analyzer.analyze_recipe_cost(
            recipe_ingredients,
            self.ingredients,
            yield_servings,
            dessert.preparation_time_minutes
        )
        
        # Step 4: Check budget constraint
        if cost_analysis.total_cost_per_serving > budget_per_unit:
            # Try to optimize for cost
            recipe_ingredients = self._optimize_for_budget(
                recipe_ingredients,
                budget_per_unit,
                yield_servings,
                dietary_constraints
            )
            # Recalculate
            cost_analysis = self.cost_analyzer.analyze_recipe_cost(
                recipe_ingredients,
                self.ingredients,
                yield_servings,
                dessert.preparation_time_minutes
            )
        
        # Step 5: Generate instructions
        instructions = self._generate_instructions(
            dessert,
            component_formulations
        )
        
        # Step 6: Run predictive simulation
        predictive_analysis = self.simulator.simulate_recipe(
            recipe_ingredients,
            self.ingredients,
            dessert
        )
        
        # Step 7: Calculate nutritional info
        nutritional_info = self._calculate_nutrition(
            recipe_ingredients,
            self.ingredients,
            yield_servings
        )
        
        # Step 8: Collect allergens and dietary labels
        allergens = self._collect_allergens(recipe_ingredients)
        dietary_labels = self._determine_dietary_labels(
            recipe_ingredients,
            dietary_constraints
        )
        
        # Step 9: Create recipe object
        recipe = Recipe(
            id=f"{dessert_type}_v1_{hash(str(request)) % 10000}",
            dessert_id=dessert.id,
            dessert_name=dessert.name,
            version="1.0",
            ingredients=recipe_ingredients,
            instructions=instructions,
            yield_servings=yield_servings,
            preparation_time_minutes=dessert.preparation_time_minutes,
            baking_time_minutes=dessert.baking_time_minutes,
            total_time_minutes=(
                dessert.preparation_time_minutes +
                (dessert.baking_time_minutes or 0)
            ),
            sustainability=sustainability,
            cost_analysis=cost_analysis,
            nutritional_info=nutritional_info,
            predictive_analysis=predictive_analysis,
            dietary_labels=dietary_labels,
            allergen_warnings=allergens,
            storage_instructions=self._get_storage_instructions(dessert_type),
            shelf_life_days=self._get_shelf_life(dessert_type),
            scaling_notes="Recipe can be scaled linearly up to 5x",
            formulation_parameters=request
        )
        
        return recipe.to_dict()
    
    def _formulate_component(
        self,
        component,
        dietary_constraints: List[str],
        sustainability_priority: str
    ) -> Dict:
        """Formulate a single dessert component"""
        
        # Match ingredients for each required function
        matched_ingredients = {}
        for function in component.required_functions:
            candidates = self.ingredient_matcher.find_ingredients_by_role(
                function,
                dietary_constraints
            )
            
            if not candidates:
                raise ValueError(
                    f"No suitable ingredients found for {function.value} "
                    f"with constraints {dietary_constraints}"
                )
            
            # Select best candidate based on priority
            best = self._select_best_ingredient(
                candidates,
                sustainability_priority
            )
            matched_ingredients[function] = best
        
        # Calculate amounts based on component requirements
        ingredients = self._calculate_component_amounts(
            matched_ingredients,
            component
        )
        
        return {
            'component_name': component.name,
            'ingredients': ingredients,
            'functions_covered': list(matched_ingredients.keys())
        }
    
    def _select_best_ingredient(
        self,
        candidates: List[Ingredient],
        priority: str
    ) -> Ingredient:
        """Select best ingredient based on optimization priority"""
        
        if priority == 'low_co2':
            return min(
                candidates,
                key=lambda x: x.sustainability.co2_kg_per_kg
            )
        elif priority == 'low_water':
            return min(
                candidates,
                key=lambda x: x.sustainability.water_liters_per_kg
            )
        elif priority == 'low_cost':
            return min(candidates, key=lambda x: x.cost_per_kg_eur)
        else:  # balanced
            # Score based on normalized metrics
            def score(ing):
                co2_score = ing.sustainability.co2_kg_per_kg / 5.0
                water_score = ing.sustainability.water_liters_per_kg / 5000.0
                cost_score = ing.cost_per_kg_eur / 20.0
                return co2_score + water_score + cost_score
            
            return min(candidates, key=score)
    
    def _calculate_component_amounts(
        self,
        matched_ingredients: Dict,
        component
    ) -> List[RecipeIngredient]:
        """Calculate ingredient amounts for a component"""
        
        # This is simplified - in production, use food chemistry models
        ingredients = []
        
        # Base amounts for common patterns
        if component.name == "Choux Pastry Shell":
            ingredients = [
                RecipeIngredient(
                    "water", "Water", 250, Unit.MILLILITER
                ),
                RecipeIngredient(
                    "vegan_butter", "Plant-Based Butter",
                    100, Unit.GRAM, "cubed"
                ),
                RecipeIngredient(
                    "all_purpose_flour", "All-Purpose Flour",
                    150, Unit.GRAM, "sifted"
                ),
                RecipeIngredient(
                    "aquafaba", "Aquafaba",
                    200, Unit.MILLILITER, "room temperature"
                ),
                RecipeIngredient(
                    "salt", "Fine Sea Salt", 2, Unit.GRAM
                )
            ]
        elif component.name == "Pastry Cream Filling":
            ingredients = [
                RecipeIngredient(
                    "coconut_cream", "Coconut Cream",
                    400, Unit.MILLILITER
                ),
                RecipeIngredient(
                    "cane_sugar", "Organic Cane Sugar",
                    80, Unit.GRAM
                ),
                RecipeIngredient(
                    "cornstarch", "Cornstarch",
                    30, Unit.GRAM
                ),
                RecipeIngredient(
                    "vanilla_extract", "Pure Vanilla Extract",
                    10, Unit.MILLILITER
                ),
                RecipeIngredient(
                    "salt", "Fine Sea Salt", 1, Unit.GRAM
                )
            ]
        elif component.name == "Chocolate Glaze":
            ingredients = [
                RecipeIngredient(
                    "cocoa_powder", "Dutch-Process Cocoa Powder",
                    40, Unit.GRAM
                ),
                RecipeIngredient(
                    "coconut_oil_refined", "Refined Coconut Oil",
                    60, Unit.GRAM, "melted"
                ),
                RecipeIngredient(
                    "maple_syrup", "Pure Maple Syrup",
                    40, Unit.MILLILITER
                )
            ]
        elif component.name == "Custard Base":
            ingredients = [
                RecipeIngredient(
                    "coconut_cream", "Coconut Cream",
                    600, Unit.MILLILITER
                ),
                RecipeIngredient(
                    "cane_sugar", "Organic Cane Sugar",
                    100, Unit.GRAM
                ),
                RecipeIngredient(
                    "cornstarch", "Cornstarch",
                    40, Unit.GRAM
                ),
                RecipeIngredient(
                    "agar_agar", "Agar Agar Powder",
                    3, Unit.GRAM
                ),
                RecipeIngredient(
                    "vanilla_extract", "Pure Vanilla Extract",
                    10, Unit.MILLILITER
                )
            ]
        elif component.name == "Caramelized Sugar Top":
            ingredients = [
                RecipeIngredient(
                    "cane_sugar", "Organic Cane Sugar",
                    60, Unit.GRAM
                )
            ]
        
        return ingredients
    
    def _generate_instructions(
        self,
        dessert: Dessert,
        component_formulations: List[Dict]
    ) -> List[RecipeStep]:
        """Generate step-by-step instructions"""
        
        instructions = []
        step_num = 1
        
        if dessert.id == "eclair":
            instructions = [
                RecipeStep(
                    step_num := 1,
                    "Preheat oven to 200°C (400°F). Line baking sheet with parchment.",
                    5, 200, True,
                    ["Proper temperature is critical for puff"]
                ),
                RecipeStep(
                    step_num := 2,
                    "In saucepan, bring water, butter, and salt to rolling boil.",
                    5, None, True,
                    ["Butter must be fully melted before adding flour"]
                ),
                RecipeStep(
                    step_num := 3,
                    "Remove from heat. Add flour all at once, stir vigorously until dough forms ball.",
                    3, None, True,
                    ["Dough should pull away from pan sides cleanly"]
                ),
                RecipeStep(
                    step_num := 4,
                    "Return to medium heat. Cook 2-3 min, stirring constantly to dry dough.",
                    3, None, True,
                    ["This step removes excess moisture for better puff"]
                ),
                RecipeStep(
                    step_num := 5,
                    "Transfer to bowl. Let cool 5 minutes to ~60°C.",
                    5, None, False
                ),
                RecipeStep(
                    step_num := 6,
                    "Add aquafaba gradually, mixing well after each addition until smooth.",
                    10, None, True,
                    ["Dough should be glossy and hold soft peaks"]
                ),
                RecipeStep(
                    step_num := 7,
                    "Pipe 10cm logs onto prepared sheet, spacing 5cm apart.",
                    10, None, False,
                    ["Use 1.5cm round tip for uniform shells"]
                ),
                RecipeStep(
                    step_num := 8,
                    "Bake 30 minutes without opening oven. Reduce to 180°C, bake 10 more minutes.",
                    40, 200, True,
                    ["Opening oven causes collapse. Shells should be golden and firm"]
                ),
                RecipeStep(
                    step_num := 9,
                    "Turn off oven. Pierce each shell with knife. Leave in oven 10 minutes to dry.",
                    10, None, True,
                    ["This prevents sogginess"]
                ),
                RecipeStep(
                    step_num := 10,
                    "For cream: Whisk coconut cream, sugar, cornstarch, salt in saucepan.",
                    5, None, False
                ),
                RecipeStep(
                    step_num := 11,
                    "Cook over medium heat, whisking constantly until thick (5-7 min).",
                    7, None, True,
                    ["Should coat back of spoon thickly"]
                ),
                RecipeStep(
                    step_num := 12,
                    "Remove from heat. Stir in vanilla. Cover with plastic touching surface. Chill 2 hours.",
                    120, None, False
                ),
                RecipeStep(
                    step_num := 13,
                    "For glaze: Whisk cocoa, melted coconut oil, maple syrup until smooth.",
                    5, None, False
                ),
                RecipeStep(
                    step_num := 14,
                    "Slice shells horizontally. Pipe cream into bottom half. Replace top.",
                    10, None, False
                ),
                RecipeStep(
                    step_num := 15,
                    "Dip tops in chocolate glaze. Let set 15 minutes before serving.",
                    15, None, False
                )
            ]
        elif dessert.id == "creme_brulee":
            instructions = [
                RecipeStep(
                    1, "Preheat oven to 150°C (300°F).",
                    5, 150, False
                ),
                RecipeStep(
                    2, "In saucepan, whisk coconut cream, sugar, cornstarch, agar agar.",
                    5, None, False
                ),
                RecipeStep(
                    3, "Heat over medium, whisking constantly until mixture thickens and bubbles (8-10 min).",
                    10, None, True,
                    ["Don't let it boil rapidly or it may curdle"]
                ),
                RecipeStep(
                    4, "Remove from heat. Whisk in vanilla extract.",
                    1, None, False
                ),
                RecipeStep(
                    5, "Strain through fine-mesh sieve into measuring cup.",
                    3, None, False,
                    ["This ensures silky smooth texture"]
                ),
                RecipeStep(
                    6, "Divide among 6 ramekins. Place in deep baking dish.",
                    5, None, False
                ),
                RecipeStep(
                    7, "Pour hot water into dish to reach halfway up ramekins (bain-marie).",
                    5, None, True,
                    ["Water bath ensures gentle, even cooking"]
                ),
                RecipeStep(
                    8, "Bake 35-40 minutes until set but still slightly jiggly in center.",
                    40, 150, True,
                    ["Custard will firm up as it cools"]
                ),
                RecipeStep(
                    9, "Remove from water bath. Cool to room temp, then chill 4 hours.",
                    240, None, False
                ),
                RecipeStep(
                    10, "Before serving, sprinkle 1 tbsp sugar evenly on each custard.",
                    5, None, False
                ),
                RecipeStep(
                    11, "Caramelize sugar with kitchen torch until golden and bubbling.",
                    5, None, True,
                    ["Keep torch moving to avoid burning. Let cool 2 min before serving"]
                )
            ]
        
        return instructions
    
    def _optimize_for_budget(
        self,
        ingredients: List[RecipeIngredient],
        budget: float,
        servings: int,
        constraints: List[str]
    ) -> List[RecipeIngredient]:
        """Attempt to reduce cost by substituting expensive ingredients"""
        # Simplified - in production, use optimization algorithm
        return ingredients
    
    def _calculate_nutrition(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient],
        servings: int
    ) -> NutritionalInfo:
        """Calculate nutritional information"""
        # Simplified calculation
        total_calories = 250 * servings
        
        return NutritionalInfo(
            calories=total_calories / servings,
            protein_g=3.5,
            fat_g=12.0,
            carbohydrates_g=32.0,
            fiber_g=1.5,
            sugar_g=18.0,
            sodium_mg=85.0
        )
    
    def _collect_allergens(
        self,
        ingredients: List[RecipeIngredient]
    ) -> List[str]:
        """Collect all allergens from ingredients"""
        allergens = set()
        for ing in ingredients:
            if ing.ingredient_id in self.ingredients:
                allergens.update(
                    self.ingredients[ing.ingredient_id].allergens
                )
        return sorted(list(allergens))
    
    def _determine_dietary_labels(
        self,
        ingredients: List[RecipeIngredient],
        constraints: List[str]
    ) -> List[str]:
        """Determine dietary labels for recipe"""
        labels = ['vegan', 'plant-based']
        
        allergens = self._collect_allergens(ingredients)
        
        if not any(a in ['wheat', 'gluten'] for a in allergens):
            labels.append('gluten-free')
        if not any(a in ['soy'] for a in allergens):
            labels.append('soy-free')
        if not any('nut' in a.lower() for a in allergens):
            labels.append('nut-free')
        
        return labels
    
    def _get_storage_instructions(self, dessert_type: str) -> str:
        """Get storage instructions for dessert type"""
        storage = {
            'eclair': "Store unfilled shells in airtight container at room temp up to 2 days. Fill just before serving. Filled éclairs refrigerate up to 1 day.",
            'creme_brulee': "Refrigerate covered up to 3 days. Caramelize sugar just before serving for best texture."
        }
        return storage.get(dessert_type, "Refrigerate in airtight container.")
    
    def _get_shelf_life(self, dessert_type: str) -> int:
        """Get shelf life in days"""
        shelf_life = {
            'eclair': 1,
            'creme_brulee': 3
        }
        return shelf_life.get(dessert_type, 2)


# Example usage
if __name__ == "__main__":
    engine = FormulationEngine()
    
    request = {
        "dessert_type": "eclair",
        "texture": ["crispy", "creamy"],
        "dietary_constraints": ["vegan", "nut_free"],
        "budget_per_unit": 3.50,
        "sustainability_priority": "low_co2",
        "yield_servings": 12
    }
    
    result = engine.formulate(request)
    print(json.dumps(result, indent=2))
