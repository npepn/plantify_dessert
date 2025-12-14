"""
Simple API Test Script
Tests the Flask API endpoints without starting the server
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app


def test_home():
    """Test home endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Home Endpoint (GET /)")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json, indent=2)}")
        assert response.status_code == 200
        assert 'name' in response.json
        print("✅ PASSED")


def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Health Check (GET /api/health)")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/api/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json, indent=2)}")
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        print("✅ PASSED")


def test_get_ingredients():
    """Test get ingredients endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Get Ingredients (GET /api/ingredients)")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/api/ingredients')
        print(f"Status: {response.status_code}")
        data = response.json
        print(f"Success: {data['success']}")
        print(f"Count: {data['count']}")
        print(f"First 3 ingredients:")
        for ing in data['ingredients'][:3]:
            print(f"  - {ing['name']} ({ing['category']})")
        assert response.status_code == 200
        assert data['success'] == True
        assert data['count'] > 0
        print("✅ PASSED")


def test_get_desserts():
    """Test get desserts endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Get Desserts (GET /api/desserts)")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/api/desserts')
        print(f"Status: {response.status_code}")
        data = response.json
        print(f"Success: {data['success']}")
        print(f"Count: {data['count']}")
        print(f"Desserts:")
        for dessert in data['desserts']:
            print(f"  - {dessert['name']} ({dessert['difficulty']})")
        assert response.status_code == 200
        assert data['success'] == True
        assert data['count'] >= 2
        print("✅ PASSED")


def test_formulate_eclair():
    """Test formulate endpoint with éclair"""
    print("\n" + "="*60)
    print("TEST 5: Formulate Éclair (POST /api/formulate)")
    print("="*60)
    
    request_data = {
        "dessert_type": "eclair",
        "dietary_constraints": ["vegan", "nut_free"],
        "budget_per_unit": 3.50,
        "sustainability_priority": "low_co2",
        "yield_servings": 12
    }
    
    with app.test_client() as client:
        response = client.post(
            '/api/formulate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        print(f"Status: {response.status_code}")
        data = response.json
        print(f"Success: {data['success']}")
        
        if data['success']:
            recipe = data['recipe']
            print(f"\nRecipe Generated:")
            print(f"  Name: {recipe['dessert_name']}")
            print(f"  Servings: {recipe['yield_servings']}")
            print(f"  Ingredients: {len(recipe['ingredients'])}")
            print(f"  Instructions: {len(recipe['instructions'])} steps")
            print(f"  Cost/serving: €{recipe['cost_analysis']['total_cost_per_serving']:.2f}")
            print(f"  CO₂/serving: {recipe['sustainability']['co2_per_serving']:.3f} kg")
            print(f"  Success probability: {recipe['predictive_analysis']['success_probability']:.1f}%")
        
        assert response.status_code == 200
        assert data['success'] == True
        print("✅ PASSED")


def test_formulate_creme_brulee():
    """Test formulate endpoint with crème brûlée"""
    print("\n" + "="*60)
    print("TEST 6: Formulate Crème Brûlée (POST /api/formulate)")
    print("="*60)
    
    request_data = {
        "dessert_type": "creme_brulee",
        "dietary_constraints": ["vegan", "gluten_free"],
        "budget_per_unit": 2.50,
        "sustainability_priority": "balanced",
        "yield_servings": 6
    }
    
    with app.test_client() as client:
        response = client.post(
            '/api/formulate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        print(f"Status: {response.status_code}")
        data = response.json
        print(f"Success: {data['success']}")
        
        if data['success']:
            recipe = data['recipe']
            print(f"\nRecipe Generated:")
            print(f"  Name: {recipe['dessert_name']}")
            print(f"  Servings: {recipe['yield_servings']}")
            print(f"  Ingredients: {len(recipe['ingredients'])}")
            print(f"  Cost/serving: €{recipe['cost_analysis']['total_cost_per_serving']:.2f}")
            print(f"  Sustainability grade: {recipe['sustainability']['sustainability_grade']}")
        
        assert response.status_code == 200
        assert data['success'] == True
        print("✅ PASSED")


def test_invalid_dessert():
    """Test error handling with invalid dessert"""
    print("\n" + "="*60)
    print("TEST 7: Error Handling (Invalid Dessert)")
    print("="*60)
    
    request_data = {
        "dessert_type": "invalid_dessert",
        "dietary_constraints": ["vegan"],
        "budget_per_unit": 5.0,
        "yield_servings": 10
    }
    
    with app.test_client() as client:
        response = client.post(
            '/api/formulate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        print(f"Status: {response.status_code}")
        data = response.json
        print(f"Success: {data['success']}")
        print(f"Error: {data.get('error', 'N/A')}")
        
        assert response.status_code == 400
        assert data['success'] == False
        print("✅ PASSED (Error handled correctly)")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  PLANTIFY DESSERT - API ENDPOINT TESTS")
    print("="*60)
    print("\n  Testing Flask API endpoints without starting server")
    
    tests = [
        test_home,
        test_health,
        test_get_ingredients,
        test_get_desserts,
        test_formulate_eclair,
        test_formulate_creme_brulee,
        test_invalid_dessert
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"\n  Total Tests: {len(tests)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n  🎉 All API tests passed successfully!")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed")
    
    print("\n" + "="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
