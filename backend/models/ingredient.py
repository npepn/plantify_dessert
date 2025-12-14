"""
Ingredient Model
Represents plant-based ingredients with their functional properties,
sustainability metrics, and cost data.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IngredientCategory(Enum):
    """Categories of ingredients based on primary function"""
    FAT = "fat"
    PROTEIN = "protein"
    EMULSIFIER = "emulsifier"
    SWEETENER = "sweetener"
    FLOUR = "flour"
    LIQUID = "liquid"
    LEAVENING = "leavening"
    STABILIZER = "stabilizer"
    FLAVORING = "flavoring"


class FunctionalRole(Enum):
    """Functional roles ingredients can play in desserts"""
    FAT_STRUCTURING = "fat_structuring"  # Lamination, mouthfeel
    EMULSIFICATION = "emulsification"    # Binding water and fat
    FOAMING = "foaming"                  # Aeration, volume
    BINDING = "binding"                  # Structure, cohesion
    BROWNING = "browning"                # Maillard reaction, caramelization
    SWEETENING = "sweetening"            # Taste, texture
    THICKENING = "thickening"            # Viscosity, stability
    MOISTURE_RETENTION = "moisture_retention"  # Shelf life, texture
    FLAVOR_CARRIER = "flavor_carrier"    # Taste delivery
    CRYSTALLIZATION = "crystallization"  # Texture control


@dataclass
class SustainabilityMetrics:
    """Environmental impact metrics per kg of ingredient"""
    co2_kg_per_kg: float  # kg CO₂e per kg ingredient
    water_liters_per_kg: float  # liters of water per kg
    land_m2_per_kg: float  # m² of land per kg
    source: str = ""  # Data source reference
    
    def __post_init__(self):
        """Validate metrics are non-negative"""
        if self.co2_kg_per_kg < 0 or self.water_liters_per_kg < 0 or self.land_m2_per_kg < 0:
            raise ValueError("Sustainability metrics must be non-negative")


@dataclass
class PhysicalProperties:
    """Physical and chemical properties relevant to baking"""
    melting_point_celsius: Optional[float] = None
    protein_content_percent: Optional[float] = None
    fat_content_percent: Optional[float] = None
    water_content_percent: Optional[float] = None
    ph: Optional[float] = None
    viscosity_cps: Optional[float] = None  # Centipoise
    emulsifying_capacity: Optional[float] = None  # 0-1 scale
    foaming_capacity: Optional[float] = None  # 0-1 scale
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Ingredient:
    """
    Comprehensive ingredient model for plant-based dessert formulation
    """
    id: str
    name: str
    category: IngredientCategory
    functional_roles: List[FunctionalRole]
    properties: PhysicalProperties
    sustainability: SustainabilityMetrics
    cost_per_kg_eur: float
    allergens: List[str] = field(default_factory=list)
    availability: str = "common"  # common, specialty, rare
    substitutes: List[str] = field(default_factory=list)  # IDs of substitute ingredients
    notes: str = ""
    
    def __post_init__(self):
        """Validate ingredient data"""
        if self.cost_per_kg_eur < 0:
            raise ValueError(f"Cost must be non-negative for {self.name}")
        
        if not self.functional_roles:
            raise ValueError(f"At least one functional role required for {self.name}")
    
    def has_role(self, role: FunctionalRole) -> bool:
        """Check if ingredient can perform a specific functional role"""
        return role in self.functional_roles
    
    def has_allergen(self, allergen: str) -> bool:
        """Check if ingredient contains a specific allergen"""
        return allergen.lower() in [a.lower() for a in self.allergens]
    
    def is_suitable_for_constraints(self, dietary_constraints: List[str]) -> bool:
        """
        Check if ingredient meets dietary constraints
        
        Args:
            dietary_constraints: List of constraints (e.g., ['vegan', 'nut_free'])
        
        Returns:
            True if ingredient meets all constraints
        """
        # All ingredients in this system are vegan by default
        if 'vegan' in dietary_constraints:
            pass  # Already satisfied
        
        # Check allergen constraints
        allergen_constraints = {
            'nut_free': ['almond', 'cashew', 'hazelnut', 'walnut', 'pecan', 'pistachio'],
            'soy_free': ['soy'],
            'gluten_free': ['wheat', 'barley', 'rye', 'gluten'],
            'coconut_free': ['coconut']
        }
        
        for constraint, allergens in allergen_constraints.items():
            if constraint in dietary_constraints:
                for allergen in allergens:
                    if self.has_allergen(allergen):
                        return False
        
        return True
    
    def calculate_impact(self, amount_kg: float) -> Dict[str, float]:
        """
        Calculate environmental impact for a given amount
        
        Args:
            amount_kg: Amount of ingredient in kg
        
        Returns:
            Dictionary with CO₂, water, and land use
        """
        return {
            'co2_kg': self.sustainability.co2_kg_per_kg * amount_kg,
            'water_liters': self.sustainability.water_liters_per_kg * amount_kg,
            'land_m2': self.sustainability.land_m2_per_kg * amount_kg
        }
    
    def calculate_cost(self, amount_kg: float) -> float:
        """Calculate cost for a given amount"""
        return self.cost_per_kg_eur * amount_kg
    
    def to_dict(self) -> Dict:
        """Convert ingredient to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'functional_roles': [role.value for role in self.functional_roles],
            'properties': self.properties.to_dict(),
            'sustainability': {
                'co2_kg_per_kg': self.sustainability.co2_kg_per_kg,
                'water_liters_per_kg': self.sustainability.water_liters_per_kg,
                'land_m2_per_kg': self.sustainability.land_m2_per_kg,
                'source': self.sustainability.source
            },
            'cost_per_kg_eur': self.cost_per_kg_eur,
            'allergens': self.allergens,
            'availability': self.availability,
            'substitutes': self.substitutes,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Ingredient':
        """Create ingredient from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            category=IngredientCategory(data['category']),
            functional_roles=[FunctionalRole(role) for role in data['functional_roles']],
            properties=PhysicalProperties(**data['properties']),
            sustainability=SustainabilityMetrics(**data['sustainability']),
            cost_per_kg_eur=data['cost_per_kg_eur'],
            allergens=data.get('allergens', []),
            availability=data.get('availability', 'common'),
            substitutes=data.get('substitutes', []),
            notes=data.get('notes', '')
        )
    
    def __repr__(self) -> str:
        return f"Ingredient(id='{self.id}', name='{self.name}', category={self.category.value})"


# Example usage and testing
if __name__ == "__main__":
    # Create a sample ingredient
    coconut_oil = Ingredient(
        id="coconut_oil_refined",
        name="Refined Coconut Oil",
        category=IngredientCategory.FAT,
        functional_roles=[
            FunctionalRole.FAT_STRUCTURING,
            FunctionalRole.MOISTURE_RETENTION,
            FunctionalRole.FLAVOR_CARRIER
        ],
        properties=PhysicalProperties(
            melting_point_celsius=24.0,
            fat_content_percent=100.0,
            water_content_percent=0.0
        ),
        sustainability=SustainabilityMetrics(
            co2_kg_per_kg=2.5,
            water_liters_per_kg=2500,
            land_m2_per_kg=7.5,
            source="Poore & Nemecek, 2018"
        ),
        cost_per_kg_eur=8.50,
        allergens=["coconut"],
        availability="common",
        notes="Excellent for lamination due to high melting point"
    )
    
    print(coconut_oil)
    print(f"Has fat structuring role: {coconut_oil.has_role(FunctionalRole.FAT_STRUCTURING)}")
    print(f"Suitable for nut-free: {coconut_oil.is_suitable_for_constraints(['nut_free'])}")
    print(f"Impact for 0.5kg: {coconut_oil.calculate_impact(0.5)}")
    print(f"Cost for 0.5kg: €{coconut_oil.calculate_cost(0.5):.2f}")
