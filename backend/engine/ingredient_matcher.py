"""
Ingredient Matcher
Finds suitable plant-based ingredients based on functional requirements.
"""

from typing import List, Dict, Optional
from models.ingredient import Ingredient, FunctionalRole


class IngredientMatcher:
    """
    Matches ingredients to functional roles with constraint filtering
    """
    
    def __init__(self, ingredients_db: Dict[str, Ingredient]):
        """
        Initialize matcher with ingredient database
        
        Args:
            ingredients_db: Dictionary of ingredient_id -> Ingredient
        """
        self.ingredients_db = ingredients_db
        
        # Build reverse index: role -> list of ingredient IDs
        self.role_index = self._build_role_index()
    
    def _build_role_index(self) -> Dict[FunctionalRole, List[str]]:
        """Build index mapping roles to ingredient IDs"""
        index = {role: [] for role in FunctionalRole}
        
        for ing_id, ingredient in self.ingredients_db.items():
            for role in ingredient.functional_roles:
                index[role].append(ing_id)
        
        return index
    
    def find_ingredients_by_role(
        self,
        role: FunctionalRole,
        dietary_constraints: Optional[List[str]] = None,
        availability: Optional[str] = None
    ) -> List[Ingredient]:
        """
        Find ingredients that can perform a specific functional role
        
        Args:
            role: The functional role needed
            dietary_constraints: List of dietary constraints
            availability: Filter by availability (common, specialty, rare)
        
        Returns:
            List of suitable ingredients, sorted by performance
        """
        if dietary_constraints is None:
            dietary_constraints = []
        
        # Get candidate ingredient IDs
        candidate_ids = self.role_index.get(role, [])
        
        # Filter by constraints
        candidates = []
        for ing_id in candidate_ids:
            ingredient = self.ingredients_db[ing_id]
            
            # Check dietary constraints
            if not ingredient.is_suitable_for_constraints(
                dietary_constraints
            ):
                continue
            
            # Check availability
            if availability and ingredient.availability != availability:
                continue
            
            candidates.append(ingredient)
        
        # Sort by performance for this role
        candidates = self._rank_by_performance(candidates, role)
        
        return candidates
    
    def _rank_by_performance(
        self,
        ingredients: List[Ingredient],
        role: FunctionalRole
    ) -> List[Ingredient]:
        """
        Rank ingredients by their performance in a specific role
        
        Uses ingredient properties to estimate effectiveness
        """
        def performance_score(ingredient: Ingredient) -> float:
            """Calculate performance score for ingredient in role"""
            score = 1.0
            props = ingredient.properties
            
            # Role-specific scoring
            if role == FunctionalRole.EMULSIFICATION:
                if props.emulsifying_capacity:
                    score = props.emulsifying_capacity
            
            elif role == FunctionalRole.FOAMING:
                if props.foaming_capacity:
                    score = props.foaming_capacity
            
            elif role == FunctionalRole.FAT_STRUCTURING:
                if props.fat_content_percent:
                    # Higher fat content = better structuring
                    score = props.fat_content_percent / 100.0
            
            elif role == FunctionalRole.THICKENING:
                if props.viscosity_cps:
                    # Higher viscosity = better thickening
                    score = min(1.0, props.viscosity_cps / 10000.0)
            
            elif role == FunctionalRole.BINDING:
                if props.protein_content_percent:
                    # Higher protein = better binding
                    score = props.protein_content_percent / 20.0
            
            # Bonus for common availability
            if ingredient.availability == "common":
                score *= 1.1
            
            return score
        
        # Sort by score (descending)
        return sorted(
            ingredients,
            key=performance_score,
            reverse=True
        )
    
    def find_substitutes(
        self,
        ingredient_id: str,
        dietary_constraints: Optional[List[str]] = None
    ) -> List[Ingredient]:
        """
        Find substitute ingredients for a given ingredient
        
        Args:
            ingredient_id: ID of ingredient to substitute
            dietary_constraints: Dietary constraints to respect
        
        Returns:
            List of suitable substitutes
        """
        if ingredient_id not in self.ingredients_db:
            return []
        
        original = self.ingredients_db[ingredient_id]
        
        # Get explicitly listed substitutes
        explicit_subs = []
        for sub_id in original.substitutes:
            if sub_id in self.ingredients_db:
                sub = self.ingredients_db[sub_id]
                if dietary_constraints:
                    if sub.is_suitable_for_constraints(dietary_constraints):
                        explicit_subs.append(sub)
                else:
                    explicit_subs.append(sub)
        
        # Find ingredients with overlapping functional roles
        role_based_subs = []
        for role in original.functional_roles:
            candidates = self.find_ingredients_by_role(
                role,
                dietary_constraints
            )
            for candidate in candidates:
                if candidate.id != ingredient_id:
                    # Check if it covers most of the original's roles
                    overlap = len(
                        set(candidate.functional_roles) &
                        set(original.functional_roles)
                    )
                    if overlap >= len(original.functional_roles) * 0.6:
                        role_based_subs.append(candidate)
        
        # Combine and deduplicate
        all_subs = explicit_subs + role_based_subs
        seen = set()
        unique_subs = []
        for sub in all_subs:
            if sub.id not in seen:
                seen.add(sub.id)
                unique_subs.append(sub)
        
        return unique_subs
    
    def find_multi_role_ingredients(
        self,
        roles: List[FunctionalRole],
        dietary_constraints: Optional[List[str]] = None
    ) -> List[Ingredient]:
        """
        Find ingredients that can perform multiple roles
        
        Useful for simplifying recipes
        
        Args:
            roles: List of required functional roles
            dietary_constraints: Dietary constraints
        
        Returns:
            Ingredients that cover multiple roles
        """
        if not roles:
            return []
        
        # Find ingredients that have all required roles
        candidates = []
        for ingredient in self.ingredients_db.values():
            # Check if ingredient has all required roles
            if all(role in ingredient.functional_roles for role in roles):
                # Check constraints
                if dietary_constraints:
                    if ingredient.is_suitable_for_constraints(
                        dietary_constraints
                    ):
                        candidates.append(ingredient)
                else:
                    candidates.append(ingredient)
        
        # Sort by number of additional roles (versatility)
        candidates.sort(
            key=lambda x: len(x.functional_roles),
            reverse=True
        )
        
        return candidates
    
    def explain_ingredient_choice(
        self,
        ingredient: Ingredient,
        role: FunctionalRole
    ) -> str:
        """
        Generate explanation for why ingredient was chosen for role
        
        Args:
            ingredient: The chosen ingredient
            role: The functional role it's filling
        
        Returns:
            Human-readable explanation
        """
        explanations = {
            FunctionalRole.FAT_STRUCTURING: (
                f"{ingredient.name} provides fat structuring with "
                f"{ingredient.properties.fat_content_percent:.1f}% fat content"
            ),
            FunctionalRole.EMULSIFICATION: (
                f"{ingredient.name} acts as emulsifier, binding water and "
                f"fat phases together"
            ),
            FunctionalRole.FOAMING: (
                f"{ingredient.name} creates foam and aeration, "
                f"essential for light texture"
            ),
            FunctionalRole.BINDING: (
                f"{ingredient.name} provides binding and structure through "
                f"protein content"
            ),
            FunctionalRole.THICKENING: (
                f"{ingredient.name} thickens the mixture, "
                f"creating desired consistency"
            ),
            FunctionalRole.BROWNING: (
                f"{ingredient.name} enables Maillard reaction and "
                f"caramelization for color and flavor"
            ),
            FunctionalRole.SWEETENING: (
                f"{ingredient.name} provides sweetness and affects texture"
            ),
            FunctionalRole.MOISTURE_RETENTION: (
                f"{ingredient.name} retains moisture, "
                f"extending shelf life and maintaining texture"
            ),
            FunctionalRole.FLAVOR_CARRIER: (
                f"{ingredient.name} carries and enhances flavors"
            ),
            FunctionalRole.CRYSTALLIZATION: (
                f"{ingredient.name} controls crystallization for "
                f"proper texture development"
            )
        }
        
        base_explanation = explanations.get(
            role,
            f"{ingredient.name} performs {role.value} function"
        )
        
        # Add property details if available
        props = ingredient.properties
        details = []
        
        if props.melting_point_celsius:
            details.append(
                f"melting point {props.melting_point_celsius}°C"
            )
        if props.emulsifying_capacity and role == FunctionalRole.EMULSIFICATION:
            details.append(
                f"emulsifying capacity {props.emulsifying_capacity:.0%}"
            )
        if props.foaming_capacity and role == FunctionalRole.FOAMING:
            details.append(
                f"foaming capacity {props.foaming_capacity:.0%}"
            )
        
        if details:
            base_explanation += f" ({', '.join(details)})"
        
        # Add sustainability note
        if ingredient.sustainability.co2_kg_per_kg < 2.0:
            base_explanation += ". Low environmental impact."
        
        return base_explanation


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    import json
    
    # Load ingredients
    db_path = Path(__file__).parent.parent / "data" / "ingredients_database.json"
    with open(db_path) as f:
        data = json.load(f)
    
    ingredients = {}
    for ing_data in data['ingredients']:
        ing = Ingredient.from_dict(ing_data)
        ingredients[ing.id] = ing
    
    # Create matcher
    matcher = IngredientMatcher(ingredients)
    
    # Test: Find emulsifiers
    print("=== Emulsifiers (nut-free) ===")
    emulsifiers = matcher.find_ingredients_by_role(
        FunctionalRole.EMULSIFICATION,
        dietary_constraints=['vegan', 'nut_free']
    )
    for ing in emulsifiers:
        print(f"- {ing.name}")
        print(f"  {matcher.explain_ingredient_choice(ing, FunctionalRole.EMULSIFICATION)}")
    
    # Test: Find substitutes
    print("\n=== Substitutes for Coconut Oil ===")
    subs = matcher.find_substitutes('coconut_oil_refined', ['vegan'])
    for sub in subs:
        print(f"- {sub.name}")
    
    # Test: Multi-role ingredients
    print("\n=== Ingredients for Fat + Emulsification ===")
    multi = matcher.find_multi_role_ingredients(
        [FunctionalRole.FAT_STRUCTURING, FunctionalRole.EMULSIFICATION],
        ['vegan']
    )
    for ing in multi:
        print(f"- {ing.name}: {[r.value for r in ing.functional_roles]}")
