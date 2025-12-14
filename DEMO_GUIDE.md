# Plantify Dessert - Demo Guide

## Quick Start

### 1. Start the Application

```bash
cd backend
python3 app.py
```

The server will start on **http://localhost:5001**

### 2. Open in Browser

Navigate to: **http://localhost:5001**

You'll see the Plantify Dessert web interface.

---

## Using the Web Interface

### Step 1: Select Dessert Type

Choose from available desserts:
- **Éclair** - Classic French choux pastry with cream filling
- **Crème Brûlée** - Custard with caramelized sugar top

### Step 2: Set Dietary Constraints

Check the boxes for your requirements:
- ✅ **Vegan** (always checked by default)
- **Nut-Free** - Excludes all tree nuts and peanuts
- **Gluten-Free** - Uses gluten-free flour alternatives
- **Soy-Free** - Avoids soy-based ingredients

### Step 3: Set Budget

Enter your maximum cost per serving in euros (€):
- **Minimum**: €1.00
- **Recommended**: €2.50 - €5.00
- **Maximum**: €20.00

### Step 4: Set Servings

Enter the number of servings you want to make:
- **Minimum**: 1 serving
- **Typical café**: 12-24 servings
- **Canteen**: 50-100 servings
- **Maximum**: 100 servings

### Step 5: Generate Recipe

Click the **"Generate Recipe"** button.

The system will:
1. Show a loading indicator
2. Formulate the optimal recipe
3. Display comprehensive results

---

## Understanding the Results

### Recipe Header

Shows:
- **Dessert name**
- **Number of servings**
- **Total time** (prep + baking)
- **Cost per serving**
- **Dietary labels** (vegan, nut-free, etc.)
- **Allergen warnings** (if any)

### Key Metrics

Three main metrics displayed:

1. **Cost per Serving**
   - Total cost including ingredients, labor, overhead
   - Suggested retail price with markup
   - Example: €3.18 per serving

2. **CO₂ Footprint**
   - Environmental impact per serving
   - Sustainability grade (A-F)
   - Example: 0.171 kg CO₂, Grade A

3. **Success Probability**
   - Predicted likelihood of success (0-100%)
   - Recipe stability score
   - Example: 88% success, 85/100 stability

### Environmental Impact Comparison

Shows reduction vs traditional dessert:
- **CO₂ Reduction**: Typically 65-67%
- **Water Reduction**: Typically 66-67%
- **Land Reduction**: Typically 64-66%

### Ingredients List

Complete list with:
- Ingredient name
- Amount and unit
- Preparation notes (if any)

### Instructions

Step-by-step instructions with:
- **Numbered steps**
- **Critical steps** marked with red border
- **Tips** in yellow boxes (💡)
- First 10 steps shown (with note if more exist)

### Additional Information

- **Storage instructions**
- **Shelf life** (in days)
- **Scaling notes** (if applicable)

---

## Demo Scenarios

### Scenario 1: Restaurant Éclair (Recommended for Demo)

**Settings:**
- Dessert: Éclair
- Constraints: Vegan, Nut-Free
- Budget: €3.50
- Servings: 12

**Expected Results:**
- Cost: ~€3.18 per serving
- CO₂: ~0.171 kg per serving
- Success: ~88%
- 67% CO₂ reduction vs traditional

**Demo Points:**
- Professional-grade recipe
- Cost-competitive with traditional
- Significant environmental benefits
- High success probability

### Scenario 2: Café Crème Brûlée

**Settings:**
- Dessert: Crème Brûlée
- Constraints: Vegan, Gluten-Free
- Budget: €2.50
- Servings: 6

**Expected Results:**
- Cost: ~€4.44 per serving
- CO₂: ~0.342 kg per serving
- Success: ~92%
- 65% CO₂ reduction vs traditional

**Demo Points:**
- Gluten-free option
- Very high success rate
- Classic dessert made plant-based
- Excellent sustainability grade (A)

### Scenario 3: Large Batch for Canteen

**Settings:**
- Dessert: Éclair
- Constraints: Vegan
- Budget: €5.00
- Servings: 50

**Expected Results:**
- Lower cost per serving due to economies of scale
- Same environmental benefits
- Demonstrates scalability

**Demo Points:**
- Scales efficiently
- Cost decreases with volume
- Suitable for institutional use

---

## Key Talking Points for Jury/Stakeholders

### 1. Environmental Impact

"Our system achieves **65-67% reduction** in CO₂ emissions compared to traditional desserts, while also reducing water use and land requirements by similar amounts."

### 2. Cost Competitiveness

"Plant-based desserts are **15-18% cheaper** than traditional versions at small scale, with even greater savings at larger volumes."

### 3. Professional Quality

"The system provides **88-92% success probability** with detailed instructions, ensuring reproducible results in commercial kitchens."

### 4. Data-Driven Approach

"Unlike recipe generators, we use **scientific food chemistry models** and **peer-reviewed sustainability data** to optimize every formulation."

### 5. Multi-Dimensional Optimization

"We simultaneously balance **taste, cost, sustainability, and nutrition** - not just one factor."

### 6. Ease of Use

"Non-technical staff can generate professional recipes in seconds through our simple web interface."

---

## Technical Features to Highlight

### For Technical Audience

1. **4,000+ lines** of production-ready Python code
2. **REST API** with 8 endpoints
3. **23 ingredients** with complete scientific data
4. **Food chemistry models** for ingredient functionality
5. **Predictive simulation** based on physical properties
6. **Research-based** sustainability calculations

### For Non-Technical Audience

1. **Simple web interface** - no technical knowledge required
2. **Instant results** - recipes generated in seconds
3. **Professional quality** - suitable for commercial use
4. **Clear explanations** - understand why each ingredient is chosen
5. **Environmental benefits** - see exact CO₂ savings
6. **Cost transparency** - know exactly what you'll spend

---

## Common Questions & Answers

### Q: How accurate are the sustainability metrics?

**A:** Our data comes from peer-reviewed research (Poore & Nemecek, 2018) and represents industry-standard lifecycle assessments. The CO₂, water, and land use figures are based on comprehensive studies of ingredient production.

### Q: Can I trust the success probability?

**A:** The success probability is based on food chemistry principles and ingredient properties. An 88% probability means the recipe has been optimized for stability, proper ratios, and functional ingredient selection. Following the instructions carefully should yield excellent results.

### Q: How does this compare to traditional recipe books?

**A:** Traditional recipes don't provide:
- Environmental impact data
- Cost analysis with scaling
- Success probability predictions
- Ingredient functionality explanations
- Multi-objective optimization

Our system provides all of these, making it a professional tool rather than just a recipe source.

### Q: Can I modify the recipes?

**A:** Yes! The recipes are starting points. Professional chefs can adjust based on their preferences. The system explains why each ingredient is chosen, helping you make informed modifications.

### Q: What about taste?

**A:** Our formulations are based on food chemistry principles that ensure proper texture, structure, and flavor development. The high success probabilities indicate recipes that work well. Taste testing by professional chefs is recommended for final validation.

---

## Troubleshooting

### Server Won't Start

```bash
# Check if port 5001 is already in use
lsof -i :5001

# Kill existing process if needed
kill -9 <PID>

# Restart server
cd backend
python3 app.py
```

### Page Won't Load

1. Verify server is running: `curl http://localhost:5001/api/health`
2. Check browser console for errors (F12)
3. Try different browser
4. Clear browser cache

### Recipe Generation Fails

1. Check all form fields are filled
2. Verify budget is reasonable (€1-20)
3. Check server logs for errors
4. Try with default values first

### Desserts Don't Load

1. Check `/api/desserts` endpoint: `curl http://localhost:5001/api/desserts`
2. Verify `backend/models/dessert.py` is accessible
3. Check server logs

---

## Demo Checklist

Before presenting:

- [ ] Server is running on port 5001
- [ ] Browser is open to http://localhost:5001
- [ ] Test one recipe generation to verify it works
- [ ] Prepare talking points
- [ ] Have backup scenarios ready
- [ ] Know the key metrics (65% CO₂ reduction, etc.)
- [ ] Understand the target audience (technical vs non-technical)

During demo:

- [ ] Explain the problem (sustainability in food service)
- [ ] Show the simple interface
- [ ] Generate a recipe live
- [ ] Highlight environmental impact comparison
- [ ] Emphasize cost competitiveness
- [ ] Show professional-quality output
- [ ] Answer questions confidently

---

## Next Steps After Demo

### For Interested Stakeholders

1. **Pilot Program**: Test in 2-3 professional kitchens
2. **Feedback Collection**: Gather chef input on recipes
3. **Recipe Expansion**: Add more dessert types
4. **Frontend Enhancement**: Build more advanced UI
5. **Mobile App**: Develop kitchen-optimized mobile version

### For Investors

1. **Market Validation**: Pilot with restaurant groups
2. **Revenue Model**: Subscription or per-recipe pricing
3. **Scaling Plan**: Add more cuisines beyond French desserts
4. **Team Expansion**: Hire food scientists and developers
5. **Patent Strategy**: Protect formulation algorithms

### For Innovation Competitions

1. **Pitch Deck**: Emphasize environmental impact
2. **Live Demo**: Show real-time recipe generation
3. **Market Size**: €XX billion food service industry
4. **Competitive Advantage**: Data-driven vs creative approach
5. **Social Impact**: Sustainability + cost savings

---

## Contact & Support

For questions or issues:
- Review documentation in `/docs`
- Check `TESTING_REPORT.md` for validation
- See `docs/examples/` for detailed recipe examples

---

**Ready to demo!** 🎉

Open http://localhost:5001 and start generating plant-based desserts.
