"""
Dessert Model
Represents French dessert types with their requirements and constraints.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from models.ingredient import FunctionalRole


class DessertCategory(Enum):
    """Categories of French desserts"""
    CHOUX = "choux"  # Éclairs, profiteroles
    LAMINATED = "laminated"  # Croissants, puff pastry
    TART = "tart"
    LAYERED = "layered"  # Mille-feuille
    MACARON = "macaron"
    CUSTARD = "custard"  # Crème brûlée
    MOUSSE = "mousse"
    CAKE = "cake"


class TextureProfile(Enum):
    """Desired texture characteristics"""
    CRISPY = "crispy"
    FLAKY = "flaky"
    CREAMY = "creamy"
    AIRY = "airy"
    SMOOTH = "smooth"
    CRUNCHY = "crunchy"
    SOFT = "soft"
    CHEWY = "chewy"


class DifficultyLevel(Enum):
    """Technical difficulty for professional kitchens"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class ComponentRequirements:
    """Requirements for a dessert component (e.g., shell, filling)"""
    name: str
    required_functions: List[FunctionalRole]
    texture_targets: List[TextureProfile]
    typical_ratio_percent: float  # Percentage of total dessert
    critical_properties: Dict[str, tuple] = field(default_factory=dict)
    # e.g., {'fat_content': (20, 40)} means 20-40% fat content
    
    def validate_properties(self, properties: Dict) -> List[str]:
        """
        Validate if properties meet requirements
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        for prop, (min_val, max_val) in self.critical_properties.items():
            if prop in properties:
                value = properties[prop]
                if value < min_val or value > max_val:
                    errors.append(
                        f"{prop} {value} outside range "
                        f"[{min_val}, {max_val}]"
                    )
        return errors


@dataclass
class Dessert:
    """
    Comprehensive dessert model for formulation
    """
    id: str
    name: str
    category: DessertCategory
    components: List[ComponentRequirements]
    difficulty: DifficultyLevel
    typical_yield: int  # Number of servings
    preparation_time_minutes: int
    baking_temp_celsius: Optional[int] = None
    baking_time_minutes: Optional[int] = None
    special_equipment: List[str] = field(default_factory=list)
    critical_techniques: List[str] = field(default_factory=list)
    common_failures: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)
    notes: str = ""
    
    def get_all_required_functions(self) -> List[FunctionalRole]:
        """Get all functional roles needed across all components"""
        functions = set()
        for component in self.components:
            functions.update(component.required_functions)
        return list(functions)
    
    def get_texture_profile(self) -> List[TextureProfile]:
        """Get all desired textures across components"""
        textures = set()
        for component in self.components:
            textures.update(component.texture_targets)
        return list(textures)
    
    def estimate_complexity_score(self) -> float:
        """
        Calculate complexity score (0-100)
        Based on components, techniques, and difficulty
        """
        base_score = {
            DifficultyLevel.BEGINNER: 20,
            DifficultyLevel.INTERMEDIATE: 40,
            DifficultyLevel.ADVANCED: 60,
            DifficultyLevel.EXPERT: 80
        }[self.difficulty]
        
        # Add complexity for multiple components
        component_score = len(self.components) * 5
        
        # Add complexity for special techniques
        technique_score = len(self.critical_techniques) * 3
        
        total = min(100, base_score + component_score + technique_score)
        return total
    
    def to_dict(self) -> Dict:
        """Convert dessert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'components': [
                {
                    'name': comp.name,
                    'required_functions': [
                        f.value for f in comp.required_functions
                    ],
                    'texture_targets': [
                        t.value for t in comp.texture_targets
                    ],
                    'typical_ratio_percent': comp.typical_ratio_percent,
                    'critical_properties': comp.critical_properties
                }
                for comp in self.components
            ],
            'difficulty': self.difficulty.value,
            'typical_yield': self.typical_yield,
            'preparation_time_minutes': self.preparation_time_minutes,
            'baking_temp_celsius': self.baking_temp_celsius,
            'baking_time_minutes': self.baking_time_minutes,
            'special_equipment': self.special_equipment,
            'critical_techniques': self.critical_techniques,
            'common_failures': self.common_failures,
            'success_indicators': self.success_indicators,
            'complexity_score': self.estimate_complexity_score(),
            'notes': self.notes
        }
    
    def __repr__(self) -> str:
        return (
            f"Dessert(id='{self.id}', name='{self.name}', "
            f"category={self.category.value})"
        )


# Predefined dessert templates
def create_eclair_template() -> Dessert:
    """Create template for vegan éclair"""
    return Dessert(
        id="eclair",
        name="Éclair",
        category=DessertCategory.CHOUX,
        components=[
            ComponentRequirements(
                name="Choux Pastry Shell",
                required_functions=[
                    FunctionalRole.FAT_STRUCTURING,
                    FunctionalRole.FOAMING,
                    FunctionalRole.BINDING,
                    FunctionalRole.MOISTURE_RETENTION
                ],
                texture_targets=[TextureProfile.CRISPY, TextureProfile.AIRY],
                typical_ratio_percent=40,
                critical_properties={
                    'fat_content': (15, 25),
                    'water_content': (50, 60),
                    'protein_content': (8, 12)
                }
            ),
            ComponentRequirements(
                name="Pastry Cream Filling",
                required_functions=[
                    FunctionalRole.THICKENING,
                    FunctionalRole.EMULSIFICATION,
                    FunctionalRole.FLAVOR_CARRIER,
                    FunctionalRole.MOISTURE_RETENTION
                ],
                texture_targets=[TextureProfile.CREAMY, TextureProfile.SMOOTH],
                typical_ratio_percent=50,
                critical_properties={
                    'fat_content': (8, 15),
                    'viscosity_cps': (5000, 15000)
                }
            ),
            ComponentRequirements(
                name="Chocolate Glaze",
                required_functions=[
                    FunctionalRole.FAT_STRUCTURING,
                    FunctionalRole.CRYSTALLIZATION,
                    FunctionalRole.FLAVOR_CARRIER
                ],
                texture_targets=[TextureProfile.SMOOTH],
                typical_ratio_percent=10,
                critical_properties={
                    'fat_content': (30, 40)
                }
            )
        ],
        difficulty=DifficultyLevel.INTERMEDIATE,
        typical_yield=12,
        preparation_time_minutes=90,
        baking_temp_celsius=200,
        baking_time_minutes=30,
        special_equipment=["piping bag", "pastry tips"],
        critical_techniques=[
            "choux paste preparation",
            "proper piping technique",
            "steam management during baking",
            "pastry cream tempering"
        ],
        common_failures=[
            "shells collapse after baking (insufficient structure)",
            "shells don't puff (too much fat or moisture)",
            "cream is too thin (insufficient thickening)",
            "glaze is grainy (improper chocolate tempering)"
        ],
        success_indicators=[
            "hollow, crispy shells",
            "smooth, stable cream",
            "glossy glaze",
            "no sogginess after filling"
        ],
        notes="Critical: proper steam in oven for initial puff"
    )


def create_creme_brulee_template() -> Dessert:
    """Create template for vegan crème brûlée"""
    return Dessert(
        id="creme_brulee",
        name="Crème Brûlée",
        category=DessertCategory.CUSTARD,
        components=[
            ComponentRequirements(
                name="Custard Base",
                required_functions=[
                    FunctionalRole.THICKENING,
                    FunctionalRole.EMULSIFICATION,
                    FunctionalRole.BINDING,
                    FunctionalRole.FLAVOR_CARRIER
                ],
                texture_targets=[
                    TextureProfile.CREAMY,
                    TextureProfile.SMOOTH
                ],
                typical_ratio_percent=90,
                critical_properties={
                    'fat_content': (15, 25),
                    'protein_content': (3, 6),
                    'viscosity_cps': (3000, 8000)
                }
            ),
            ComponentRequirements(
                name="Caramelized Sugar Top",
                required_functions=[
                    FunctionalRole.CRYSTALLIZATION,
                    FunctionalRole.BROWNING
                ],
                texture_targets=[TextureProfile.CRUNCHY],
                typical_ratio_percent=10,
                critical_properties={}
            )
        ],
        difficulty=DifficultyLevel.INTERMEDIATE,
        typical_yield=6,
        preparation_time_minutes=60,
        baking_temp_celsius=150,
        baking_time_minutes=40,
        special_equipment=["ramekins", "kitchen torch", "water bath"],
        critical_techniques=[
            "gentle heating to avoid curdling",
            "water bath (bain-marie) baking",
            "proper caramelization technique",
            "temperature control"
        ],
        common_failures=[
            "custard curdles (too high temperature)",
            "custard doesn't set (insufficient thickener)",
            "sugar burns instead of caramelizes",
            "watery texture (improper emulsification)"
        ],
        success_indicators=[
            "smooth, set custard with slight jiggle",
            "even caramelized sugar crust",
            "no bubbles or cracks",
            "clean release from ramekin"
        ],
        notes="Coconut cream base works excellently for richness"
    )


def create_croissant_template() -> Dessert:
    """Create template for vegan croissant"""
    return Dessert(
        id="croissant",
        name="Croissant",
        category=DessertCategory.LAMINATED,
        components=[
            ComponentRequirements(
                name="Laminated Dough",
                required_functions=[
                    FunctionalRole.FAT_STRUCTURING,
                    FunctionalRole.BINDING,
                    FunctionalRole.MOISTURE_RETENTION
                ],
                texture_targets=[TextureProfile.FLAKY, TextureProfile.CRISPY],
                typical_ratio_percent=100,
                critical_properties={
                    'fat_content': (25, 35),
                    'water_content': (35, 45)
                }
            )
        ],
        difficulty=DifficultyLevel.EXPERT,
        typical_yield=12,
        preparation_time_minutes=180,
        baking_temp_celsius=200,
        baking_time_minutes=20,
        special_equipment=["rolling pin", "pastry brush"],
        critical_techniques=[
            "lamination technique",
            "proper folding",
            "temperature control",
            "resting periods"
        ],
        common_failures=[
            "butter breaks through dough",
            "layers don't separate",
            "dough is too tough"
        ],
        success_indicators=[
            "distinct flaky layers",
            "golden brown color",
            "airy interior"
        ],
        notes="Requires precise temperature control and multiple resting periods"
    )


def create_tart_template() -> Dessert:
    """Create template for vegan tart"""
    return Dessert(
        id="tart",
        name="Fruit Tart",
        category=DessertCategory.TART,
        components=[
            ComponentRequirements(
                name="Tart Shell",
                required_functions=[
                    FunctionalRole.FAT_STRUCTURING,
                    FunctionalRole.BINDING
                ],
                texture_targets=[TextureProfile.CRISPY, TextureProfile.CRUNCHY],
                typical_ratio_percent=40,
                critical_properties={
                    'fat_content': (30, 40)
                }
            ),
            ComponentRequirements(
                name="Pastry Cream",
                required_functions=[
                    FunctionalRole.THICKENING,
                    FunctionalRole.EMULSIFICATION
                ],
                texture_targets=[TextureProfile.CREAMY],
                typical_ratio_percent=60,
                critical_properties={
                    'fat_content': (10, 20)
                }
            )
        ],
        difficulty=DifficultyLevel.INTERMEDIATE,
        typical_yield=8,
        preparation_time_minutes=90,
        baking_temp_celsius=180,
        baking_time_minutes=25,
        special_equipment=["tart pan", "pie weights"],
        critical_techniques=[
            "blind baking",
            "even rolling",
            "proper crimping"
        ],
        common_failures=[
            "soggy bottom",
            "shrinking crust",
            "cracking"
        ],
        success_indicators=[
            "crisp shell",
            "smooth cream",
            "no gaps"
        ],
        notes="Blind baking essential for crisp crust"
    )


def create_macaron_template() -> Dessert:
    """Create template for vegan macaron"""
    return Dessert(
        id="macaron",
        name="Macaron",
        category=DessertCategory.MACARON,
        components=[
            ComponentRequirements(
                name="Macaron Shell",
                required_functions=[
                    FunctionalRole.FOAMING,
                    FunctionalRole.BINDING,
                    FunctionalRole.CRYSTALLIZATION
                ],
                texture_targets=[TextureProfile.SMOOTH, TextureProfile.CHEWY],
                typical_ratio_percent=70,
                critical_properties={
                    'protein_content': (5, 10)
                }
            ),
            ComponentRequirements(
                name="Filling",
                required_functions=[
                    FunctionalRole.EMULSIFICATION,
                    FunctionalRole.FLAVOR_CARRIER
                ],
                texture_targets=[TextureProfile.CREAMY],
                typical_ratio_percent=30,
                critical_properties={
                    'fat_content': (40, 60)
                }
            )
        ],
        difficulty=DifficultyLevel.EXPERT,
        typical_yield=24,
        preparation_time_minutes=120,
        baking_temp_celsius=150,
        baking_time_minutes=15,
        special_equipment=["piping bag", "silicone mat"],
        critical_techniques=[
            "macaronage technique",
            "proper piping",
            "resting before baking",
            "temperature precision"
        ],
        common_failures=[
            "no feet formation",
            "hollow shells",
            "cracked tops",
            "uneven baking"
        ],
        success_indicators=[
            "smooth tops",
            "ruffled feet",
            "chewy texture"
        ],
        notes="Extremely technique-sensitive, requires practice"
    )


def create_mousse_template() -> Dessert:
    """Create template for vegan mousse"""
    return Dessert(
        id="mousse",
        name="Chocolate Mousse",
        category=DessertCategory.MOUSSE,
        components=[
            ComponentRequirements(
                name="Mousse Base",
                required_functions=[
                    FunctionalRole.FOAMING,
                    FunctionalRole.EMULSIFICATION,
                    FunctionalRole.THICKENING
                ],
                texture_targets=[TextureProfile.AIRY, TextureProfile.CREAMY],
                typical_ratio_percent=100,
                critical_properties={
                    'fat_content': (15, 25)
                }
            )
        ],
        difficulty=DifficultyLevel.INTERMEDIATE,
        typical_yield=6,
        preparation_time_minutes=30,
        baking_temp_celsius=None,
        baking_time_minutes=None,
        special_equipment=["whisk", "mixing bowls"],
        critical_techniques=[
            "proper folding",
            "temperature control",
            "aeration technique"
        ],
        common_failures=[
            "deflated mousse",
            "grainy texture",
            "separation"
        ],
        success_indicators=[
            "light and airy",
            "holds shape",
            "smooth texture"
        ],
        notes="No baking required, must chill to set"
    )


# Example usage
if __name__ == "__main__":
    eclair = create_eclair_template()
    print(eclair)
    print(f"Required functions: {eclair.get_all_required_functions()}")
    print(f"Complexity score: {eclair.estimate_complexity_score()}")
    print(f"\nTexture profile: {eclair.get_texture_profile()}")
