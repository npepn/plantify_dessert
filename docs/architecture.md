# Plantify Dessert - System Architecture

## Overview

Plantify Dessert is a full-stack web application designed for professional kitchens to formulate plant-based French desserts with data-driven optimization.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │ Input Forms  │  │ Output Panels│      │
│  │              │  │              │  │              │      │
│  │ - Overview   │  │ - Dessert    │  │ - Recipe     │      │
│  │ - Quick      │  │   Selection  │  │ - Metrics    │      │
│  │   Actions    │  │ - Constraints│  │ - Cost       │      │
│  │              │  │ - Budget     │  │ - Comparison │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API (JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask/Python)                    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Layer (Flask Routes)                   │ │
│  │  /api/formulate  /api/ingredients  /api/desserts       │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Core Engine Layer                          │ │
│  │                                                          │ │
│  │  ┌──────────────────┐  ┌──────────────────┐           │ │
│  │  │  Formulation     │  │  Ingredient      │           │ │
│  │  │  Engine          │  │  Matcher         │           │ │
│  │  │                  │  │                  │           │ │
│  │  │ - Recipe logic   │  │ - Functional     │           │ │
│  │  │ - Optimization   │  │   substitution   │           │ │
│  │  │ - Validation     │  │ - Role matching  │           │ │
│  │  └──────────────────┘  └──────────────────┘           │ │
│  │                                                          │ │
│  │  ┌──────────────────┐  ┌──────────────────┐           │ │
│  │  │  Sustainability  │  │  Cost            │           │ │
│  │  │  Calculator      │  │  Analyzer        │           │ │
│  │  │                  │  │                  │           │ │
│  │  │ - CO₂ footprint  │  │ - Unit cost      │           │ │
│  │  │ - Water use      │  │ - Batch scaling  │           │ │
│  │  │ - Land use       │  │ - Alternatives   │           │ │
│  │  └──────────────────┘  └──────────────────┘           │ │
│  │                                                          │ │
│  │  ┌──────────────────┐                                  │ │
│  │  │  Predictive      │                                  │ │
│  │  │  Simulator       │                                  │ │
│  │  │                  │                                  │ │
│  │  │ - Texture model  │                                  │ │
│  │  │ - Stability      │                                  │ │
│  │  │ - Risk warnings  │                                  │ │
│  │  └──────────────────┘                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Data Layer (SQLAlchemy)                    │ │
│  │                                                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │Ingredient│  │ Dessert  │  │  Recipe  │            │ │
│  │  │  Model   │  │  Model   │  │  Model   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              Database (SQLite/PostgreSQL)                    │
│                                                               │
│  - Ingredients (properties, sustainability, cost)            │
│  - Dessert templates (requirements, constraints)             │
│  - Recipe history (formulations, results)                    │
│  - User preferences                                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: React 18+, Material-UI, Recharts

**Components**:
- **Dashboard**: Overview, recent recipes, quick actions
- **Input Forms**: Dessert selection, constraint specification
- **Output Panels**: Recipe display, metrics visualization, cost breakdown
- **Comparison View**: Traditional vs plant-based side-by-side

**Key Features**:
- Responsive design for tablets (kitchen use)
- Real-time validation
- Interactive charts for sustainability metrics
- Print-friendly recipe output

### 2. API Layer

**Technology**: Flask, Flask-CORS, Flask-RESTful

**Endpoints**:

```
POST   /api/formulate          - Generate optimized recipe
GET    /api/ingredients        - List available ingredients
GET    /api/ingredients/:id    - Get ingredient details
GET    /api/desserts           - List supported desserts
GET    /api/desserts/:id       - Get dessert requirements
POST   /api/simulate           - Run predictive simulation
GET    /api/compare            - Compare traditional vs plant-based
POST   /api/scale              - Scale recipe to different batch sizes
```

### 3. Core Engine Layer

#### 3.1 Formulation Engine

**Purpose**: Generate optimized plant-based recipes

**Logic**:
1. Parse user requirements (dessert type, constraints, budget)
2. Identify required ingredient functions (fat, emulsifier, aerator, etc.)
3. Match plant-based ingredients to functions
4. Calculate optimal ratios using food chemistry models
5. Validate against constraints
6. Generate reproducible recipe

**Key Algorithms**:
- Functional role mapping
- Multi-objective optimization (taste, cost, sustainability)
- Constraint satisfaction

#### 3.2 Ingredient Matcher

**Purpose**: Find plant-based substitutes based on functionality

**Functional Categories**:
- **Fat Structuring**: Coconut oil, cocoa butter, vegan butter
- **Emulsification**: Soy lecithin, sunflower lecithin, aquafaba
- **Foaming/Aeration**: Aquafaba, soy protein, pea protein
- **Binding**: Flax meal, chia seeds, psyllium husk
- **Browning**: Maple syrup, coconut sugar, date syrup
- **Creaminess**: Coconut cream, cashew cream, oat cream

**Matching Logic**:
```python
def match_ingredient(function, constraints):
    candidates = filter_by_function(function)
    candidates = filter_by_allergens(candidates, constraints)
    candidates = filter_by_availability(candidates)
    return rank_by_performance(candidates)
```

#### 3.3 Sustainability Calculator

**Purpose**: Calculate environmental impact

**Metrics**:
- **CO₂ Footprint**: kg CO₂e per kg ingredient
- **Water Use**: liters per kg ingredient
- **Land Use**: m² per kg ingredient

**Data Sources**:
- IPCC reports
- Water Footprint Network
- Academic research (Poore & Nemecek, 2018)

**Calculation**:
```
Total Impact = Σ(ingredient_amount × ingredient_impact_factor)
```

#### 3.4 Cost Analyzer

**Purpose**: Calculate and optimize costs

**Features**:
- Per-unit cost calculation
- Batch scaling (20, 50, 100, 500+ units)
- Regional price variations
- Bulk discount modeling
- Alternative ingredient suggestions when over budget

**Formula**:
```
Unit Cost = Σ(ingredient_amount × ingredient_price) + labor_cost + overhead
```

#### 3.5 Predictive Simulator

**Purpose**: Predict recipe outcomes

**Models**:
- **Dough Elasticity**: Based on protein content, hydration, fat ratio
- **Cream Stability**: Emulsifier concentration, fat content, temperature
- **Lamination Success**: Fat melting point, dough hydration, layer count
- **Baking Behavior**: Leavening agents, moisture content, temperature

**Output**:
- Success probability (0-100%)
- Risk warnings
- Adjustment suggestions

### 4. Data Layer

**Technology**: SQLAlchemy ORM

**Models**:

#### Ingredient Model
```python
class Ingredient:
    id: int
    name: str
    category: str
    functions: List[str]  # emulsifier, aerator, etc.
    properties: Dict      # melting_point, protein_content, etc.
    sustainability: Dict  # co2, water, land
    cost_per_kg: float
    allergens: List[str]
    availability: str
```

#### Dessert Model
```python
class Dessert:
    id: int
    name: str
    category: str
    required_functions: List[str]
    texture_profile: Dict
    typical_ingredients: List[str]
    difficulty: str
```

#### Recipe Model
```python
class Recipe:
    id: int
    dessert_id: int
    ingredients: List[Dict]  # {ingredient_id, amount, unit}
    instructions: List[str]
    yield_amount: int
    sustainability_score: Dict
    cost_per_unit: float
    created_at: datetime
```

### 5. Database Schema

```sql
-- Ingredients table
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    functions JSON,
    properties JSON,
    sustainability JSON,
    cost_per_kg DECIMAL(10,2),
    allergens JSON,
    availability VARCHAR(20)
);

-- Desserts table
CREATE TABLE desserts (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    required_functions JSON,
    texture_profile JSON,
    typical_ingredients JSON,
    difficulty VARCHAR(20)
);

-- Recipes table
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    dessert_id INTEGER,
    ingredients JSON,
    instructions JSON,
    yield_amount INTEGER,
    sustainability_score JSON,
    cost_per_unit DECIMAL(10,2),
    created_at TIMESTAMP,
    FOREIGN KEY (dessert_id) REFERENCES desserts(id)
);
```

## Data Flow

### Recipe Formulation Flow

```
User Input
    ↓
[Validate Input]
    ↓
[Identify Required Functions] ← Dessert Template
    ↓
[Match Ingredients] ← Ingredient Database
    ↓
[Calculate Ratios] ← Food Chemistry Models
    ↓
[Optimize] ← Multi-objective Algorithm
    ↓
[Calculate Sustainability] ← Impact Factors
    ↓
[Calculate Cost] ← Price Database
    ↓
[Run Simulation] ← Predictive Models
    ↓
[Generate Recipe]
    ↓
Output (JSON)
```

## Scalability Considerations

### Performance
- Caching for ingredient database queries
- Async processing for complex optimizations
- Database indexing on frequently queried fields

### Deployment
- Docker containerization
- Horizontal scaling with load balancer
- CDN for frontend assets
- Database replication for read-heavy operations

## Security

- Input validation and sanitization
- Rate limiting on API endpoints
- HTTPS only
- CORS configuration
- SQL injection prevention (ORM)

## Future Enhancements

1. **Machine Learning**: Learn from user feedback to improve formulations
2. **Batch Processing**: Generate multiple recipe variations simultaneously
3. **Supplier Integration**: Real-time pricing from ingredient suppliers
4. **Mobile App**: Native iOS/Android for kitchen use
5. **Collaboration**: Multi-user recipe development
6. **Sensory Analysis**: Integration with taste testing data

## Technology Justification

### Why Python/Flask?
- Excellent for scientific computing (NumPy, SciPy)
- Rich ecosystem for data processing
- Easy integration with ML libraries
- Fast development cycle

### Why React?
- Component reusability
- Large ecosystem (Material-UI, Recharts)
- Excellent performance
- Strong community support

### Why SQLite/PostgreSQL?
- SQLite: Easy development setup
- PostgreSQL: Production-grade reliability
- Both support JSON fields for flexible data
- Strong SQLAlchemy support

## Conclusion

This architecture provides a solid foundation for a professional-grade plant-based dessert formulation tool, balancing functionality, performance, and maintainability.
