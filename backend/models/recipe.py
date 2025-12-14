"""
Recipe Model
Represents a formulated plant-based dessert recipe with all metadata.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class Unit(Enum):
    """Measurement units for ingredients"""
    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    LITER = "l"
    TEASPOON = "tsp"
    TABLESPOON = "tbsp"
    CUP = "cup"
    PIECE = "piece"


@dataclass
class RecipeIngredient:
    """An ingredient with its amount in a recipe"""
    ingredient_id: str
    ingredient_name: str
    amount: float
    unit: Unit
    preparation_notes: str = ""  # e.g., "melted", "room temperature"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient_name,
            'amount': self.amount,
            'unit': self.unit.value,
            'preparation_notes': self.preparation_notes
        }


@dataclass
class RecipeStep:
    """A single step in recipe instructions"""
    step_number: int
    instruction: str
    duration_minutes: Optional[int] = None
    temperature_celsius: Optional[int] = None
    critical: bool = False  # Mark critical steps
    tips: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'step_number': self.step_number,
            'instruction': self.instruction,
            'duration_minutes': self.duration_minutes,
            'temperature_celsius': self.temperature_celsius,
            'critical': self.critical,
            'tips': self.tips
        }


@dataclass
class SustainabilityScore:
    """Environmental impact scores for a recipe"""
    total_co2_kg: float
    total_water_liters: float
    total_land_m2: float
    co2_per_serving: float
    water_per_serving: float
    land_per_serving: float
    comparison_to_traditional: Dict[str, float] = field(
        default_factory=dict
    )
    # e.g., {'co2_reduction_percent': 65, 'water_reduction_percent': 45}
    
    def get_sustainability_grade(self) -> str:
        """
        Calculate overall sustainability grade (A-F)
        Based on CO₂ per serving
        """
        co2 = self.co2_per_serving
        if co2 < 0.5:
            return "A"
        elif co2 < 1.0:
            return "B"
        elif co2 < 2.0:
            return "C"
        elif co2 < 3.0:
            return "D"
        elif co2 < 5.0:
            return "E"
        else:
            return "F"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'total_co2_kg': round(self.total_co2_kg, 3),
            'total_water_liters': round(self.total_water_liters, 2),
            'total_land_m2': round(self.total_land_m2, 3),
            'co2_per_serving': round(self.co2_per_serving, 3),
            'water_per_serving': round(self.water_per_serving, 2),
            'land_per_serving': round(self.land_per_serving, 3),
            'sustainability_grade': self.get_sustainability_grade(),
            'comparison_to_traditional': self.comparison_to_traditional
        }


@dataclass
class CostAnalysis:
    """Cost breakdown for a recipe"""
    ingredient_cost_total: float
    ingredient_cost_per_serving: float
    labor_cost_estimate: float
    overhead_cost_estimate: float
    total_cost_per_serving: float
    suggested_retail_price: float  # With typical markup
    profit_margin_percent: float
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    # e.g., {'flour': 2.50, 'sugar': 1.20, ...}
    
    def is_within_budget(self, budget_per_serving: float) -> bool:
        """Check if recipe meets budget constraint"""
        return self.total_cost_per_serving <= budget_per_serving
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ingredient_cost_total': round(self.ingredient_cost_total, 2),
            'ingredient_cost_per_serving': round(
                self.ingredient_cost_per_serving, 2
            ),
            'labor_cost_estimate': round(self.labor_cost_estimate, 2),
            'overhead_cost_estimate': round(self.overhead_cost_estimate, 2),
            'total_cost_per_serving': round(
                self.total_cost_per_serving, 2
            ),
            'suggested_retail_price': round(self.suggested_retail_price, 2),
            'profit_margin_percent': round(self.profit_margin_percent, 1),
            'cost_breakdown': {
                k: round(v, 2) for k, v in self.cost_breakdown.items()
            }
        }


@dataclass
class NutritionalInfo:
    """Nutritional information per serving"""
    calories: float
    protein_g: float
    fat_g: float
    carbohydrates_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'calories': round(self.calories, 0),
            'protein_g': round(self.protein_g, 1),
            'fat_g': round(self.fat_g, 1),
            'carbohydrates_g': round(self.carbohydrates_g, 1),
            'fiber_g': round(self.fiber_g, 1),
            'sugar_g': round(self.sugar_g, 1),
            'sodium_mg': round(self.sodium_mg, 0)
        }


@dataclass
class PredictiveAnalysis:
    """Predicted outcomes and risk assessment"""
    success_probability: float  # 0-100
    texture_prediction: Dict[str, str]
    # e.g., {'shell': 'crispy', 'filling': 'creamy'}
    stability_score: float  # 0-100
    risk_warnings: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'success_probability': round(self.success_probability, 1),
            'texture_prediction': self.texture_prediction,
            'stability_score': round(self.stability_score, 1),
            'risk_warnings': self.risk_warnings,
            'optimization_suggestions': self.optimization_suggestions
        }


@dataclass
class Recipe:
    """
    Complete recipe with all formulation data and analysis
    """
    id: str
    dessert_id: str
    dessert_name: str
    version: str
    ingredients: List[RecipeIngredient]
    instructions: List[RecipeStep]
    yield_servings: int
    preparation_time_minutes: int
    baking_time_minutes: Optional[int]
    total_time_minutes: int
    sustainability: SustainabilityScore
    cost_analysis: CostAnalysis
    nutritional_info: NutritionalInfo
    predictive_analysis: PredictiveAnalysis
    dietary_labels: List[str] = field(default_factory=list)
    # e.g., ['vegan', 'nut_free', 'gluten_free']
    allergen_warnings: List[str] = field(default_factory=list)
    storage_instructions: str = ""
    shelf_life_days: int = 3
    scaling_notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    formulation_parameters: Dict = field(default_factory=dict)
    # Store original request parameters
    
    def scale_recipe(self, target_servings: int) -> 'Recipe':
        """
        Scale recipe to different serving size
        
        Args:
            target_servings: Desired number of servings
        
        Returns:
            New Recipe instance with scaled amounts
        """
        scale_factor = target_servings / self.yield_servings
        
        # Scale ingredients
        scaled_ingredients = []
        for ing in self.ingredients:
            scaled_ingredients.append(
                RecipeIngredient(
                    ingredient_id=ing.ingredient_id,
                    ingredient_name=ing.ingredient_name,
                    amount=ing.amount * scale_factor,
                    unit=ing.unit,
                    preparation_notes=ing.preparation_notes
                )
            )
        
        # Scale costs
        scaled_cost = CostAnalysis(
            ingredient_cost_total=(
                self.cost_analysis.ingredient_cost_total * scale_factor
            ),
            ingredient_cost_per_serving=(
                self.cost_analysis.ingredient_cost_per_serving
            ),
            labor_cost_estimate=(
                self.cost_analysis.labor_cost_estimate * scale_factor
            ),
            overhead_cost_estimate=(
                self.cost_analysis.overhead_cost_estimate * scale_factor
            ),
            total_cost_per_serving=(
                self.cost_analysis.total_cost_per_serving
            ),
            suggested_retail_price=(
                self.cost_analysis.suggested_retail_price
            ),
            profit_margin_percent=(
                self.cost_analysis.profit_margin_percent
            ),
            cost_breakdown={
                k: v * scale_factor
                for k, v in self.cost_analysis.cost_breakdown.items()
            }
        )
        
        # Scale sustainability
        scaled_sustainability = SustainabilityScore(
            total_co2_kg=self.sustainability.total_co2_kg * scale_factor,
            total_water_liters=(
                self.sustainability.total_water_liters * scale_factor
            ),
            total_land_m2=self.sustainability.total_land_m2 * scale_factor,
            co2_per_serving=self.sustainability.co2_per_serving,
            water_per_serving=self.sustainability.water_per_serving,
            land_per_serving=self.sustainability.land_per_serving,
            comparison_to_traditional=(
                self.sustainability.comparison_to_traditional
            )
        )
        
        # Create scaled recipe
        scaled_recipe = Recipe(
            id=f"{self.id}_scaled_{target_servings}",
            dessert_id=self.dessert_id,
            dessert_name=self.dessert_name,
            version=f"{self.version}_scaled",
            ingredients=scaled_ingredients,
            instructions=self.instructions,  # Instructions don't scale
            yield_servings=target_servings,
            preparation_time_minutes=self.preparation_time_minutes,
            baking_time_minutes=self.baking_time_minutes,
            total_time_minutes=self.total_time_minutes,
            sustainability=scaled_sustainability,
            cost_analysis=scaled_cost,
            nutritional_info=self.nutritional_info,
            predictive_analysis=self.predictive_analysis,
            dietary_labels=self.dietary_labels,
            allergen_warnings=self.allergen_warnings,
            storage_instructions=self.storage_instructions,
            shelf_life_days=self.shelf_life_days,
            scaling_notes=(
                f"Scaled from {self.yield_servings} to "
                f"{target_servings} servings"
            ),
            formulation_parameters=self.formulation_parameters
        )
        
        return scaled_recipe
    
    def to_dict(self) -> Dict:
        """Convert recipe to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'dessert_id': self.dessert_id,
            'dessert_name': self.dessert_name,
            'version': self.version,
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'instructions': [step.to_dict() for step in self.instructions],
            'yield_servings': self.yield_servings,
            'preparation_time_minutes': self.preparation_time_minutes,
            'baking_time_minutes': self.baking_time_minutes,
            'total_time_minutes': self.total_time_minutes,
            'sustainability': self.sustainability.to_dict(),
            'cost_analysis': self.cost_analysis.to_dict(),
            'nutritional_info': self.nutritional_info.to_dict(),
            'predictive_analysis': self.predictive_analysis.to_dict(),
            'dietary_labels': self.dietary_labels,
            'allergen_warnings': self.allergen_warnings,
            'storage_instructions': self.storage_instructions,
            'shelf_life_days': self.shelf_life_days,
            'scaling_notes': self.scaling_notes,
            'created_at': self.created_at.isoformat(),
            'formulation_parameters': self.formulation_parameters
        }
    
    def __repr__(self) -> str:
        return (
            f"Recipe(id='{self.id}', dessert='{self.dessert_name}', "
            f"servings={self.yield_servings})"
        )


# Example usage
if __name__ == "__main__":
    # Create a sample recipe
    sample_recipe = Recipe(
        id="eclair_v1",
        dessert_id="eclair",
        dessert_name="Vegan Éclair",
        version="1.0",
        ingredients=[
            RecipeIngredient(
                "water", "Water", 250, Unit.MILLILITER
            ),
            RecipeIngredient(
                "coconut_oil", "Coconut Oil", 100, Unit.GRAM, "melted"
            )
        ],
        instructions=[
            RecipeStep(
                1, "Preheat oven to 200°C", 5, 200, True
            )
        ],
        yield_servings=12,
        preparation_time_minutes=60,
        baking_time_minutes=30,
        total_time_minutes=90,
        sustainability=SustainabilityScore(
            1.2, 150, 0.5, 0.1, 12.5, 0.042
        ),
        cost_analysis=CostAnalysis(
            15.0, 1.25, 5.0, 2.0, 1.83, 5.50, 67
        ),
        nutritional_info=NutritionalInfo(
            250, 3, 12, 30, 1, 15, 50
        ),
        predictive_analysis=PredictiveAnalysis(
            85, {'shell': 'crispy'}, 90
        ),
        dietary_labels=['vegan']
    )
    
    print(sample_recipe)
    scaled = sample_recipe.scale_recipe(24)
    print(f"Scaled to {scaled.yield_servings} servings")
