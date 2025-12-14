"""
Cost Analyzer
Calculates and analyzes recipe costs with scaling support.
"""

from typing import List, Dict
from models.ingredient import Ingredient
from models.recipe import RecipeIngredient, CostAnalysis, Unit


class CostAnalyzer:
    """
    Analyzes recipe costs and provides scaling recommendations
    """
    
    # Labor cost estimates (EUR per hour)
    LABOR_RATES = {
        'beginner': 15.0,
        'intermediate': 20.0,
        'advanced': 25.0,
        'expert': 30.0
    }
    
    # Overhead multipliers (as fraction of ingredient cost)
    OVERHEAD_MULTIPLIERS = {
        'cafe': 0.15,  # 15% overhead
        'restaurant': 0.20,
        'canteen': 0.10,
        'bakery': 0.12
    }
    
    # Typical markup percentages for retail pricing
    MARKUP_PERCENTAGES = {
        'cafe': 3.0,  # 300% markup
        'restaurant': 3.5,
        'canteen': 1.5,
        'bakery': 2.5
    }
    
    def __init__(
        self,
        operation_type: str = 'cafe',
        labor_rate: float = 20.0
    ):
        """
        Initialize cost analyzer
        
        Args:
            operation_type: Type of operation (cafe, restaurant, etc.)
            labor_rate: Hourly labor rate in EUR
        """
        self.operation_type = operation_type
        self.labor_rate = labor_rate
        self.overhead_multiplier = self.OVERHEAD_MULTIPLIERS.get(
            operation_type, 0.15
        )
        self.markup = self.MARKUP_PERCENTAGES.get(operation_type, 3.0)
    
    def analyze_recipe_cost(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient],
        servings: int,
        preparation_time_minutes: int
    ) -> CostAnalysis:
        """
        Analyze complete cost structure for a recipe
        
        Args:
            ingredients: List of recipe ingredients
            ingredient_db: Database of ingredient objects
            servings: Number of servings
            preparation_time_minutes: Total prep time
        
        Returns:
            CostAnalysis with detailed breakdown
        """
        # Calculate ingredient costs
        ingredient_cost_total = 0.0
        cost_breakdown = {}
        
        for recipe_ing in ingredients:
            if recipe_ing.ingredient_id not in ingredient_db:
                continue
            
            ingredient = ingredient_db[recipe_ing.ingredient_id]
            
            # Convert to kg and calculate cost
            amount_kg = self._convert_to_kg(
                recipe_ing.amount,
                recipe_ing.unit
            )
            cost = ingredient.calculate_cost(amount_kg)
            
            ingredient_cost_total += cost
            cost_breakdown[ingredient.name] = cost
        
        # Calculate labor cost
        labor_hours = preparation_time_minutes / 60.0
        labor_cost_estimate = labor_hours * self.labor_rate
        
        # Calculate overhead
        overhead_cost_estimate = (
            ingredient_cost_total * self.overhead_multiplier
        )
        
        # Calculate per-serving costs
        ingredient_cost_per_serving = ingredient_cost_total / servings
        total_cost_per_serving = (
            (ingredient_cost_total + labor_cost_estimate + 
             overhead_cost_estimate) / servings
        )
        
        # Calculate suggested retail price
        suggested_retail_price = total_cost_per_serving * self.markup
        
        # Calculate profit margin
        profit_margin_percent = (
            (suggested_retail_price - total_cost_per_serving) /
            suggested_retail_price * 100
        )
        
        return CostAnalysis(
            ingredient_cost_total=ingredient_cost_total,
            ingredient_cost_per_serving=ingredient_cost_per_serving,
            labor_cost_estimate=labor_cost_estimate,
            overhead_cost_estimate=overhead_cost_estimate,
            total_cost_per_serving=total_cost_per_serving,
            suggested_retail_price=suggested_retail_price,
            profit_margin_percent=profit_margin_percent,
            cost_breakdown=cost_breakdown
        )
    
    def scale_cost_analysis(
        self,
        base_analysis: CostAnalysis,
        base_servings: int,
        target_servings: int,
        preparation_time_minutes: int
    ) -> CostAnalysis:
        """
        Scale cost analysis to different batch size
        
        Args:
            base_analysis: Original cost analysis
            base_servings: Original number of servings
            target_servings: Target number of servings
            preparation_time_minutes: Prep time (may not scale linearly)
        
        Returns:
            Scaled CostAnalysis
        """
        scale_factor = target_servings / base_servings
        
        # Ingredient costs scale linearly
        ingredient_cost_total = (
            base_analysis.ingredient_cost_total * scale_factor
        )
        
        # Labor costs scale sub-linearly (efficiency gains)
        labor_scale = self._calculate_labor_scale_factor(scale_factor)
        labor_cost_estimate = (
            base_analysis.labor_cost_estimate * labor_scale
        )
        
        # Overhead scales with ingredients
        overhead_cost_estimate = (
            ingredient_cost_total * self.overhead_multiplier
        )
        
        # Recalculate per-serving metrics
        ingredient_cost_per_serving = ingredient_cost_total / target_servings
        total_cost_per_serving = (
            (ingredient_cost_total + labor_cost_estimate + 
             overhead_cost_estimate) / target_servings
        )
        
        suggested_retail_price = total_cost_per_serving * self.markup
        profit_margin_percent = (
            (suggested_retail_price - total_cost_per_serving) /
            suggested_retail_price * 100
        )
        
        # Scale cost breakdown
        cost_breakdown = {
            k: v * scale_factor
            for k, v in base_analysis.cost_breakdown.items()
        }
        
        return CostAnalysis(
            ingredient_cost_total=ingredient_cost_total,
            ingredient_cost_per_serving=ingredient_cost_per_serving,
            labor_cost_estimate=labor_cost_estimate,
            overhead_cost_estimate=overhead_cost_estimate,
            total_cost_per_serving=total_cost_per_serving,
            suggested_retail_price=suggested_retail_price,
            profit_margin_percent=profit_margin_percent,
            cost_breakdown=cost_breakdown
        )
    
    def _calculate_labor_scale_factor(self, scale_factor: float) -> float:
        """
        Calculate how labor scales with batch size
        
        Labor doesn't scale linearly - there are efficiency gains
        
        Args:
            scale_factor: Ingredient scale factor
        
        Returns:
            Labor scale factor (< scale_factor for large batches)
        """
        if scale_factor <= 1.0:
            return scale_factor
        elif scale_factor <= 2.0:
            return 1.0 + (scale_factor - 1.0) * 0.8
        elif scale_factor <= 5.0:
            return 1.8 + (scale_factor - 2.0) * 0.6
        else:
            return 3.6 + (scale_factor - 5.0) * 0.4
    
    def find_cost_reduction_opportunities(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient],
        cost_breakdown: Dict[str, float],
        target_reduction_percent: float = 10.0
    ) -> List[Dict]:
        """
        Identify opportunities to reduce costs
        
        Args:
            ingredients: Recipe ingredients
            ingredient_db: Ingredient database
            cost_breakdown: Current cost breakdown
            target_reduction_percent: Target cost reduction
        
        Returns:
            List of cost reduction suggestions
        """
        suggestions = []
        
        # Sort ingredients by cost contribution
        sorted_costs = sorted(
            cost_breakdown.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_cost = sum(cost_breakdown.values())
        
        for ing_name, cost in sorted_costs[:5]:  # Top 5 expensive
            # Find the ingredient
            ingredient = None
            for recipe_ing in ingredients:
                if recipe_ing.ingredient_id in ingredient_db:
                    ing_obj = ingredient_db[recipe_ing.ingredient_id]
                    if ing_obj.name == ing_name:
                        ingredient = ing_obj
                        break
            
            if not ingredient:
                continue
            
            # Calculate cost contribution
            contribution_percent = (cost / total_cost) * 100
            
            if contribution_percent > 15:  # Significant contributor
                # Check for cheaper substitutes
                if ingredient.substitutes:
                    cheaper_subs = []
                    for sub_id in ingredient.substitutes:
                        if sub_id in ingredient_db:
                            sub = ingredient_db[sub_id]
                            if sub.cost_per_kg_eur < ingredient.cost_per_kg_eur:
                                savings = (
                                    (ingredient.cost_per_kg_eur - 
                                     sub.cost_per_kg_eur) /
                                    ingredient.cost_per_kg_eur * 100
                                )
                                cheaper_subs.append({
                                    'name': sub.name,
                                    'savings_percent': savings,
                                    'cost_per_kg': sub.cost_per_kg_eur
                                })
                    
                    if cheaper_subs:
                        suggestions.append({
                            'type': 'substitute',
                            'ingredient': ing_name,
                            'current_cost': cost,
                            'contribution_percent': contribution_percent,
                            'alternatives': cheaper_subs
                        })
                
                # Suggest bulk purchasing
                if ingredient.availability == 'common':
                    suggestions.append({
                        'type': 'bulk_purchase',
                        'ingredient': ing_name,
                        'current_cost': cost,
                        'contribution_percent': contribution_percent,
                        'potential_savings_percent': 15.0,
                        'note': 'Consider bulk purchasing for 10-15% savings'
                    })
        
        return suggestions
    
    def calculate_break_even_volume(
        self,
        cost_per_serving: float,
        retail_price: float,
        fixed_costs_monthly: float = 0.0
    ) -> int:
        """
        Calculate break-even volume
        
        Args:
            cost_per_serving: Total cost per serving
            retail_price: Selling price per serving
            fixed_costs_monthly: Monthly fixed costs (rent, etc.)
        
        Returns:
            Number of servings needed to break even
        """
        if retail_price <= cost_per_serving:
            return -1  # Never breaks even
        
        contribution_margin = retail_price - cost_per_serving
        
        if fixed_costs_monthly == 0:
            return 0  # Breaks even immediately
        
        return int(fixed_costs_monthly / contribution_margin) + 1
    
    def _convert_to_kg(self, amount: float, unit: Unit) -> float:
        """Convert ingredient amount to kilograms"""
        conversions = {
            Unit.GRAM: 0.001,
            Unit.KILOGRAM: 1.0,
            Unit.MILLILITER: 0.001,
            Unit.LITER: 1.0,
            Unit.TEASPOON: 0.005,
            Unit.TABLESPOON: 0.015,
            Unit.CUP: 0.240,
            Unit.PIECE: 0.050
        }
        return amount * conversions.get(unit, 0.001)
    
    def generate_cost_report(
        self,
        analysis: CostAnalysis,
        servings: int
    ) -> str:
        """
        Generate human-readable cost report
        
        Args:
            analysis: Cost analysis object
            servings: Number of servings
        
        Returns:
            Formatted cost report
        """
        report = []
        report.append("=== COST ANALYSIS REPORT ===\n")
        
        report.append(f"Batch Size: {servings} servings\n")
        
        report.append("\n--- Ingredient Costs ---")
        report.append(
            f"Total: €{analysis.ingredient_cost_total:.2f}"
        )
        report.append(
            f"Per Serving: €{analysis.ingredient_cost_per_serving:.2f}"
        )
        
        report.append("\n--- Top 5 Expensive Ingredients ---")
        sorted_breakdown = sorted(
            analysis.cost_breakdown.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for ing_name, cost in sorted_breakdown[:5]:
            percent = (cost / analysis.ingredient_cost_total) * 100
            report.append(f"  {ing_name}: €{cost:.2f} ({percent:.1f}%)")
        
        report.append("\n--- Additional Costs ---")
        report.append(f"Labor: €{analysis.labor_cost_estimate:.2f}")
        report.append(f"Overhead: €{analysis.overhead_cost_estimate:.2f}")
        
        report.append("\n--- Per Serving Economics ---")
        report.append(
            f"Total Cost: €{analysis.total_cost_per_serving:.2f}"
        )
        report.append(
            f"Suggested Price: €{analysis.suggested_retail_price:.2f}"
        )
        report.append(
            f"Profit Margin: {analysis.profit_margin_percent:.1f}%"
        )
        
        return "\n".join(report)


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
    
    # Sample recipe
    recipe_ingredients = [
        RecipeIngredient(
            "coconut_cream", "Coconut Cream", 400, Unit.MILLILITER
        ),
        RecipeIngredient(
            "cane_sugar", "Organic Cane Sugar", 100, Unit.GRAM
        ),
        RecipeIngredient(
            "vanilla_extract", "Pure Vanilla Extract", 10, Unit.MILLILITER
        )
    ]
    
    # Analyze costs
    analyzer = CostAnalyzer(operation_type='cafe')
    analysis = analyzer.analyze_recipe_cost(
        recipe_ingredients,
        ingredients_db,
        servings=6,
        preparation_time_minutes=60
    )
    
    print(analyzer.generate_cost_report(analysis, 6))
    
    # Test scaling
    print("\n=== SCALED TO 50 SERVINGS ===")
    scaled = analyzer.scale_cost_analysis(analysis, 6, 50, 60)
    print(f"Cost per serving: €{scaled.total_cost_per_serving:.2f}")
    print(f"Total batch cost: €{scaled.ingredient_cost_total + scaled.labor_cost_estimate + scaled.overhead_cost_estimate:.2f}")
