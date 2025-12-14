"""
Predictive Simulator
Simulates recipe outcomes and predicts success probability.
"""

from typing import List, Dict
from models.ingredient import Ingredient, FunctionalRole
from models.recipe import RecipeIngredient, PredictiveAnalysis, Unit
from models.dessert import Dessert, TextureProfile


class PredictiveSimulator:
    """
    Predicts recipe outcomes based on ingredient properties
    """
    
    def __init__(self):
        """Initialize simulator"""
        pass
    
    def simulate_recipe(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient],
        dessert: Dessert
    ) -> PredictiveAnalysis:
        """
        Simulate recipe and predict outcomes
        
        Args:
            ingredients: Recipe ingredients
            ingredient_db: Ingredient database
            dessert: Dessert template
        
        Returns:
            PredictiveAnalysis with predictions and warnings
        """
        # Calculate ingredient properties
        properties = self._calculate_recipe_properties(
            ingredients,
            ingredient_db
        )
        
        # Predict textures for each component
        texture_prediction = self._predict_textures(
            dessert,
            properties
        )
        
        # Calculate stability score
        stability_score = self._calculate_stability(
            properties,
            dessert
        )
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(
            properties,
            dessert,
            stability_score
        )
        
        # Generate risk warnings
        risk_warnings = self._generate_risk_warnings(
            properties,
            dessert,
            stability_score
        )
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimizations(
            properties,
            dessert,
            success_probability
        )
        
        return PredictiveAnalysis(
            success_probability=success_probability,
            texture_prediction=texture_prediction,
            stability_score=stability_score,
            risk_warnings=risk_warnings,
            optimization_suggestions=optimization_suggestions
        )
    
    def _calculate_recipe_properties(
        self,
        ingredients: List[RecipeIngredient],
        ingredient_db: Dict[str, Ingredient]
    ) -> Dict:
        """Calculate aggregate recipe properties"""
        total_weight = 0.0
        total_fat = 0.0
        total_protein = 0.0
        total_water = 0.0
        
        emulsifiers = []
        aerators = []
        thickeners = []
        
        for recipe_ing in ingredients:
            if recipe_ing.ingredient_id not in ingredient_db:
                continue
            
            ingredient = ingredient_db[recipe_ing.ingredient_id]
            amount_kg = self._convert_to_kg(
                recipe_ing.amount,
                recipe_ing.unit
            )
            
            total_weight += amount_kg
            
            props = ingredient.properties
            if props.fat_content_percent:
                total_fat += amount_kg * (props.fat_content_percent / 100.0)
            if props.protein_content_percent:
                total_protein += amount_kg * (props.protein_content_percent / 100.0)
            if props.water_content_percent:
                total_water += amount_kg * (props.water_content_percent / 100.0)
            
            # Collect functional ingredients
            if ingredient.has_role(FunctionalRole.EMULSIFICATION):
                emulsifiers.append(ingredient)
            if ingredient.has_role(FunctionalRole.FOAMING):
                aerators.append(ingredient)
            if ingredient.has_role(FunctionalRole.THICKENING):
                thickeners.append(ingredient)
        
        # Calculate percentages
        fat_percent = (total_fat / total_weight * 100) if total_weight > 0 else 0
        protein_percent = (total_protein / total_weight * 100) if total_weight > 0 else 0
        water_percent = (total_water / total_weight * 100) if total_weight > 0 else 0
        
        return {
            'total_weight_kg': total_weight,
            'fat_percent': fat_percent,
            'protein_percent': protein_percent,
            'water_percent': water_percent,
            'emulsifiers': emulsifiers,
            'aerators': aerators,
            'thickeners': thickeners
        }
    
    def _predict_textures(
        self,
        dessert: Dessert,
        properties: Dict
    ) -> Dict[str, str]:
        """Predict texture outcomes for each component"""
        predictions = {}
        
        for component in dessert.components:
            component_name = component.name
            
            # Predict based on component type and properties
            if "Choux" in component_name or "Shell" in component_name:
                # Choux pastry prediction
                if properties['fat_percent'] >= 15 and properties['fat_percent'] <= 25:
                    if properties['water_percent'] >= 50:
                        predictions[component_name] = "crispy and airy"
                    else:
                        predictions[component_name] = "crispy but dense"
                else:
                    predictions[component_name] = "may not puff properly"
            
            elif "Cream" in component_name or "Custard" in component_name:
                # Cream/custard prediction
                if properties['thickeners']:
                    if properties['fat_percent'] >= 10:
                        predictions[component_name] = "smooth and creamy"
                    else:
                        predictions[component_name] = "smooth but light"
                else:
                    predictions[component_name] = "may be too thin"
            
            elif "Glaze" in component_name:
                # Glaze prediction
                if properties['fat_percent'] >= 30:
                    predictions[component_name] = "glossy and smooth"
                else:
                    predictions[component_name] = "may be dull"
            
            elif "Sugar" in component_name or "Caramel" in component_name:
                predictions[component_name] = "crunchy"
            
            else:
                # Default prediction based on texture targets
                if TextureProfile.CREAMY in component.texture_targets:
                    predictions[component_name] = "creamy"
                elif TextureProfile.CRISPY in component.texture_targets:
                    predictions[component_name] = "crispy"
                else:
                    predictions[component_name] = "as expected"
        
        return predictions
    
    def _calculate_stability(
        self,
        properties: Dict,
        dessert: Dessert
    ) -> float:
        """
        Calculate stability score (0-100)
        
        Higher score = more stable formulation
        """
        score = 50.0  # Base score
        
        # Check emulsification
        if properties['emulsifiers']:
            score += 15.0
            # Bonus for multiple emulsifiers
            if len(properties['emulsifiers']) > 1:
                score += 5.0
        else:
            # Penalty if emulsification needed
            needs_emulsification = any(
                FunctionalRole.EMULSIFICATION in comp.required_functions
                for comp in dessert.components
            )
            if needs_emulsification:
                score -= 20.0
        
        # Check thickening
        if properties['thickeners']:
            score += 10.0
        
        # Check aeration
        if properties['aerators']:
            score += 10.0
        
        # Check fat content (important for structure)
        if 10 <= properties['fat_percent'] <= 40:
            score += 10.0
        elif properties['fat_percent'] < 5:
            score -= 10.0
        elif properties['fat_percent'] > 50:
            score -= 5.0
        
        # Check protein content (important for binding)
        if 3 <= properties['protein_percent'] <= 15:
            score += 5.0
        
        # Ensure score is in valid range
        return max(0.0, min(100.0, score))
    
    def _calculate_success_probability(
        self,
        properties: Dict,
        dessert: Dessert,
        stability_score: float
    ) -> float:
        """
        Calculate overall success probability (0-100)
        """
        probability = 60.0  # Base probability
        
        # Stability contributes significantly
        probability += (stability_score - 50) * 0.4
        
        # Check if all required functions are covered
        required_functions = dessert.get_all_required_functions()
        
        # Count how many functions we have ingredients for
        covered_functions = set()
        if properties['emulsifiers']:
            covered_functions.add(FunctionalRole.EMULSIFICATION)
        if properties['aerators']:
            covered_functions.add(FunctionalRole.FOAMING)
        if properties['thickeners']:
            covered_functions.add(FunctionalRole.THICKENING)
        
        coverage_ratio = len(covered_functions) / max(len(required_functions), 1)
        probability += coverage_ratio * 20
        
        # Adjust based on dessert difficulty
        difficulty_penalties = {
            'beginner': 0,
            'intermediate': -5,
            'advanced': -10,
            'expert': -15
        }
        probability += difficulty_penalties.get(dessert.difficulty.value, 0)
        
        # Ensure probability is in valid range
        return max(0.0, min(100.0, probability))
    
    def _generate_risk_warnings(
        self,
        properties: Dict,
        dessert: Dessert,
        stability_score: float
    ) -> List[str]:
        """Generate risk warnings based on analysis"""
        warnings = []
        
        # Stability warnings
        if stability_score < 40:
            warnings.append(
                "LOW STABILITY: Formulation may be unstable. "
                "Consider adding stabilizers or emulsifiers."
            )
        
        # Fat content warnings
        if properties['fat_percent'] < 5:
            warnings.append(
                "Very low fat content may result in dry texture "
                "and poor mouthfeel."
            )
        elif properties['fat_percent'] > 50:
            warnings.append(
                "Very high fat content may result in greasy texture "
                "and separation issues."
            )
        
        # Water content warnings
        if properties['water_percent'] > 70:
            warnings.append(
                "High water content may cause sogginess. "
                "Ensure proper baking/setting time."
            )
        
        # Missing functional ingredients
        if not properties['emulsifiers']:
            needs_emulsification = any(
                FunctionalRole.EMULSIFICATION in comp.required_functions
                for comp in dessert.components
            )
            if needs_emulsification:
                warnings.append(
                    "No emulsifier detected. May have separation issues."
                )
        
        if not properties['thickeners']:
            needs_thickening = any(
                FunctionalRole.THICKENING in comp.required_functions
                for comp in dessert.components
            )
            if needs_thickening:
                warnings.append(
                    "No thickener detected. Mixture may be too thin."
                )
        
        # Dessert-specific warnings
        if dessert.id == "eclair":
            if properties['water_percent'] < 45:
                warnings.append(
                    "Choux pastry needs sufficient moisture for steam. "
                    "May not puff properly."
                )
        
        return warnings
    
    def _generate_optimizations(
        self,
        properties: Dict,
        dessert: Dessert,
        success_probability: float
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if success_probability < 70:
            suggestions.append(
                "Consider testing a small batch first before "
                "scaling up production."
            )
        
        # Fat optimization
        if properties['fat_percent'] < 10:
            suggestions.append(
                "Increase fat content slightly for better texture "
                "and mouthfeel."
            )
        
        # Protein optimization
        if properties['protein_percent'] < 2:
            suggestions.append(
                "Consider adding protein-rich ingredient for "
                "better structure."
            )
        
        # Emulsification optimization
        if len(properties['emulsifiers']) == 0:
            suggestions.append(
                "Add emulsifier (e.g., lecithin) for better stability."
            )
        
        # Positive feedback
        if success_probability >= 85:
            suggestions.append(
                "Excellent formulation! High probability of success."
            )
        
        return suggestions
    
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


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    import json
    from models.dessert import create_eclair_template
    
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
        RecipeIngredient("water", "Water", 250, Unit.MILLILITER),
        RecipeIngredient("vegan_butter", "Plant-Based Butter", 100, Unit.GRAM),
        RecipeIngredient("all_purpose_flour", "All-Purpose Flour", 150, Unit.GRAM),
        RecipeIngredient("aquafaba", "Aquafaba", 200, Unit.MILLILITER)
    ]
    
    # Get dessert template
    dessert = create_eclair_template()
    
    # Run simulation
    simulator = PredictiveSimulator()
    analysis = simulator.simulate_recipe(
        recipe_ingredients,
        ingredients_db,
        dessert
    )
    
    print("=== PREDICTIVE ANALYSIS ===")
    print(f"Success Probability: {analysis.success_probability:.1f}%")
    print(f"Stability Score: {analysis.stability_score:.1f}/100")
    
    print("\n=== TEXTURE PREDICTIONS ===")
    for component, texture in analysis.texture_prediction.items():
        print(f"{component}: {texture}")
    
    print("\n=== RISK WARNINGS ===")
    for warning in analysis.risk_warnings:
        print(f"⚠️  {warning}")
    
    print("\n=== OPTIMIZATION SUGGESTIONS ===")
    for suggestion in analysis.optimization_suggestions:
        print(f"💡 {suggestion}")
