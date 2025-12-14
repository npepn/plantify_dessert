"""
Sustainability Calculator
Calculates environmental impact metrics for recipes.
"""

from typing import List, Dict
from models.ingredient import Ingredient
from models.recipe import RecipeIngredient, SustainabilityScore, Unit


class SustainabilityCalculator:
    """
    Calculates CO₂, water, and land use for recipes
    """
    
    # Traditional dessert impact data (per serving)
    # Based on research: Poore & Nemecek (2018), Water Footprint Network
    TRADITIONAL_IMPACTS = {
        'eclair': {
            'co2_kg': 0.45,  # Butter, eggs, cream
            'water_liters': 85.0,
            'land_m2': 0.18
        },
        'creme_brulee': {
            'co2_kg': 0.52,  # Heavy cream, eggs
            'water_liters': 95.0,
            'land_m2': 0.22
        },
        'croissant': {
            'co2_kg': 0.38,
            'water_liters': 75.0,
            'land_m2': 0.15
        },
        'macaron': {
            'co2_kg': 0.35,
            'water_liters': 70.0,
            'land_m2': 0.14
        }
    }
    
    def __init__(self):
        """Initialize calculator"""
        pass
    
    def calculate_recipe_impact(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient],
        servings: int
    ) -> SustainabilityScore:
        """
        Calculate total environmental impact for a recipe
        
        Args:
            ingredients: List of recipe ingredients with amounts
            ingredient_db: Database of ingredient objects
            servings: Number of servings
        
        Returns:
            SustainabilityScore with total and per-serving metrics
        """
        total_co2 = 0.0
        total_water = 0.0
        total_land = 0.0
        
        for recipe_ing in ingredients:
            if recipe_ing.ingredient_id not in ingredient_db:
                continue
            
            ingredient = ingredient_db[recipe_ing.ingredient_id]
            
            # Convert amount to kg
            amount_kg = self._convert_to_kg(
                recipe_ing.amount,
                recipe_ing.unit
            )
            
            # Calculate impact
            impact = ingredient.calculate_impact(amount_kg)
            total_co2 += impact['co2_kg']
            total_water += impact['water_liters']
            total_land += impact['land_m2']
        
        # Calculate per-serving metrics
        co2_per_serving = total_co2 / servings
        water_per_serving = total_water / servings
        land_per_serving = total_land / servings
        
        return SustainabilityScore(
            total_co2_kg=total_co2,
            total_water_liters=total_water,
            total_land_m2=total_land,
            co2_per_serving=co2_per_serving,
            water_per_serving=water_per_serving,
            land_per_serving=land_per_serving
        )
    
    def compare_to_traditional(
        self,
        plant_based_score: SustainabilityScore,
        dessert_type: str
    ) -> Dict[str, float]:
        """
        Compare plant-based recipe to traditional version
        
        Args:
            plant_based_score: Sustainability score of plant-based recipe
            dessert_type: Type of dessert (for traditional baseline)
        
        Returns:
            Dictionary with reduction percentages
        """
        # Get traditional baseline
        traditional = self.TRADITIONAL_IMPACTS.get(dessert_type)
        
        if not traditional:
            # Use average if specific dessert not found
            traditional = {
                'co2_kg': 0.40,
                'water_liters': 80.0,
                'land_m2': 0.17
            }
        
        # Calculate reductions
        co2_reduction = (
            (traditional['co2_kg'] - plant_based_score.co2_per_serving) /
            traditional['co2_kg'] * 100
        )
        
        water_reduction = (
            (traditional['water_liters'] - plant_based_score.water_per_serving) /
            traditional['water_liters'] * 100
        )
        
        land_reduction = (
            (traditional['land_m2'] - plant_based_score.land_per_serving) /
            traditional['land_m2'] * 100
        )
        
        return {
            'co2_reduction_percent': round(co2_reduction, 1),
            'water_reduction_percent': round(water_reduction, 1),
            'land_reduction_percent': round(land_reduction, 1),
            'traditional_co2_kg': traditional['co2_kg'],
            'traditional_water_liters': traditional['water_liters'],
            'traditional_land_m2': traditional['land_m2']
        }
    
    def _convert_to_kg(self, amount: float, unit: Unit) -> float:
        """
        Convert ingredient amount to kilograms
        
        Args:
            amount: Amount value
            unit: Unit of measurement
        
        Returns:
            Amount in kilograms
        """
        conversions = {
            Unit.GRAM: 0.001,
            Unit.KILOGRAM: 1.0,
            Unit.MILLILITER: 0.001,  # Assume density ~1 g/ml
            Unit.LITER: 1.0,
            Unit.TEASPOON: 0.005,  # ~5g
            Unit.TABLESPOON: 0.015,  # ~15g
            Unit.CUP: 0.240,  # ~240g
            Unit.PIECE: 0.050  # Assume ~50g per piece
        }
        
        return amount * conversions.get(unit, 0.001)
    
    def calculate_carbon_footprint_breakdown(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient]
    ) -> Dict[str, float]:
        """
        Break down CO₂ footprint by ingredient
        
        Args:
            ingredients: List of recipe ingredients
            ingredient_db: Database of ingredient objects
        
        Returns:
            Dictionary mapping ingredient name to CO₂ contribution
        """
        breakdown = {}
        
        for recipe_ing in ingredients:
            if recipe_ing.ingredient_id not in ingredient_db:
                continue
            
            ingredient = ingredient_db[recipe_ing.ingredient_id]
            amount_kg = self._convert_to_kg(
                recipe_ing.amount,
                recipe_ing.unit
            )
            
            co2 = ingredient.sustainability.co2_kg_per_kg * amount_kg
            breakdown[ingredient.name] = co2
        
        return breakdown
    
    def get_sustainability_recommendations(
        self,
        score: SustainabilityScore,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient]
    ) -> List[str]:
        """
        Generate recommendations for improving sustainability
        
        Args:
            score: Current sustainability score
            ingredients: Recipe ingredients
            ingredient_db: Ingredient database
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Analyze CO₂ footprint
        breakdown = self.calculate_carbon_footprint_breakdown(
            ingredients,
            ingredient_db
        )
        
        # Find highest impact ingredients
        if breakdown:
            sorted_impacts = sorted(
                breakdown.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Check if top contributor is >30% of total
            total_co2 = sum(breakdown.values())
            if total_co2 > 0:
                top_ingredient, top_co2 = sorted_impacts[0]
                if top_co2 / total_co2 > 0.3:
                    recommendations.append(
                        f"Consider reducing {top_ingredient} amount or "
                        f"finding lower-impact alternative "
                        f"({top_co2:.2f} kg CO₂, "
                        f"{top_co2/total_co2*100:.0f}% of total)"
                    )
        
        # Check overall grade
        grade = score.get_sustainability_grade()
        if grade in ['D', 'E', 'F']:
            recommendations.append(
                f"Current sustainability grade: {grade}. "
                f"Consider using more local, seasonal ingredients."
            )
        
        # Water usage check
        if score.water_per_serving > 50:
            recommendations.append(
                f"High water usage ({score.water_per_serving:.1f}L per serving). "
                f"Consider ingredients with lower water footprint."
            )
        
        # Land use check
        if score.land_per_serving > 0.15:
            recommendations.append(
                f"High land use ({score.land_per_serving:.2f}m² per serving). "
                f"Favor ingredients with efficient land use."
            )
        
        # Positive feedback
        if grade in ['A', 'B']:
            recommendations.append(
                f"Excellent sustainability! Grade {grade}. "
                f"This recipe has low environmental impact."
            )
        
        return recommendations
    
    def estimate_carbon_offset_equivalent(
        self,
        co2_kg: float
    ) -> Dict[str, float]:
        """
        Convert CO₂ to relatable equivalents
        
        Args:
            co2_kg: Amount of CO₂ in kg
        
        Returns:
            Dictionary with various equivalents
        """
        return {
            'km_driven': co2_kg * 5.5,  # km in average car
            'trees_needed_year': co2_kg / 21.0,  # trees for 1 year
            'smartphone_charges': co2_kg * 121,  # full charges
            'led_bulb_hours': co2_kg * 1000  # hours of LED bulb
        }


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    import json
    
    # Load ingredients
    db_path = Path(__file__).parent.parent / "data" / "ingredients_database.json"
    with open(db_path) as f:
        data = json.load(f)
    
    ingredients_db = {}
    for ing_data in data['ingredients']:
        ing = Ingredient.from_dict(ing_data)
        ingredients_db[ing.id] = ing
    
    # Create sample recipe
    recipe_ingredients = [
        RecipeIngredient(
            "coconut_cream", "Coconut Cream", 400, Unit.MILLILITER
        ),
        RecipeIngredient(
            "cane_sugar", "Organic Cane Sugar", 100, Unit.GRAM
        ),
        RecipeIngredient(
            "cornstarch", "Cornstarch", 40, Unit.GRAM
        ),
        RecipeIngredient(
            "vanilla_extract", "Pure Vanilla Extract", 10, Unit.MILLILITER
        )
    ]
    
    # Calculate impact
    calculator = SustainabilityCalculator()
    score = calculator.calculate_recipe_impact(
        recipe_ingredients,
        ingredients_db,
        servings=6
    )
    
    print("=== Sustainability Analysis ===")
    print(f"Total CO₂: {score.total_co2_kg:.3f} kg")
    print(f"Per serving: {score.co2_per_serving:.3f} kg CO₂")
    print(f"Grade: {score.get_sustainability_grade()}")
    
    # Compare to traditional
    comparison = calculator.compare_to_traditional(score, 'creme_brulee')
    print(f"\n=== vs Traditional ===")
    print(f"CO₂ reduction: {comparison['co2_reduction_percent']:.1f}%")
    print(f"Water reduction: {comparison['water_reduction_percent']:.1f}%")
    
    # Get recommendations
    recommendations = calculator.get_sustainability_recommendations(
        score,
        recipe_ingredients,
        ingredients_db
    )
    print(f"\n=== Recommendations ===")
    for rec in recommendations:
        print(f"- {rec}")
