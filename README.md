# Plantify Dessert

A professional digital tool for formulating, optimizing, and evaluating plant-based French desserts in commercial kitchens.

## Overview

Plantify Dessert is designed for restaurants, cafés, canteens, and bakeries to create data-driven, reproducible plant-based dessert recipes while balancing:

- **Taste & Texture**: Professional-grade results
- **Cost & Scalability**: From café to industrial scale
- **Environmental Sustainability**: CO₂, water, and land use optimization
- **Nutritional & Allergen Constraints**: Safe, healthy formulations

## Key Features

### 1. Recipe Formulation Engine
- Intelligent plant-based ingredient substitution
- Functional ingredient logic (emulsification, foaming, structuring)
- Optimized ratios for professional results

### 2. Sustainability Module
- CO₂ footprint calculation
- Water and land use estimation
- Traditional vs plant-based comparison

### 3. Cost & Feasibility Analysis
- Per-unit and batch costing
- Multi-scale support (20-500+ units/day)
- Budget-aware ingredient suggestions

### 4. Predictive Simulation
- Texture and stability predictions
- Baking behavior modeling
- Risk warnings for formulation issues

## Supported Desserts

- Éclairs
- Croissants & Puff Pastry
- Tarts
- Mille-feuille
- Macarons
- Crème Brûlée
- Mousse
- Choux Pastry

## Technology Stack

- **Backend**: Python 3.9+, Flask, SQLAlchemy
- **Frontend**: React, Material-UI, Recharts
- **Database**: SQLite (dev), PostgreSQL (prod)
- **API**: RESTful JSON

## Project Structure

```
plantify_dessert/
├── backend/
│   ├── models/           # Data models
│   ├── engine/           # Core formulation logic
│   ├── api/              # REST API
│   ├── data/             # Ingredient database
│   └── app.py            # Flask application
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   └── App.js        # Main application
│   └── package.json
├── docs/
│   ├── architecture.md   # System architecture
│   ├── examples/         # Worked examples
│   └── api.md            # API documentation
└── README.md
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Usage Example

```python
from engine.formulation_engine import FormulationEngine

engine = FormulationEngine()

request = {
    "dessert_type": "eclair",
    "texture": "crispy_shell_creamy_filling",
    "dietary_constraints": ["vegan", "nut_free"],
    "budget_per_unit": 2.50,
    "sustainability_priority": "low_co2"
}

result = engine.formulate(request)
print(result["recipe"])
print(result["sustainability_metrics"])
print(result["cost_analysis"])
```

## Target Users

- Professional chefs and pastry chefs
- Restaurant and café owners
- Canteen and catering managers
- Bakery operations
- Food innovation teams

## Differentiators

Unlike generic recipe generators, Plantify Dessert:
- Uses scientific ingredient functionality models
- Provides reproducible, scalable formulations
- Calculates real environmental impact
- Optimizes for commercial kitchen constraints
- Explains ingredient choices with food chemistry

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.
