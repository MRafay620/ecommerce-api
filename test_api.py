import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_api():
    """Test script to validate API functionality"""
    
    print("🧪 Starting API Tests...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Get Categories
    print("\n2. Testing Categories...")
    try:
        response = requests.get(f"{BASE_URL}/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Found {len(categories)} categories")
            if categories:
                print(f"   📋 Sample category: {categories[0]['name']}")
        else:
            print("   ❌ Failed to get categories")
    except Exception as e:
        print(f"   ❌ Categories error: {e}")
    
    # Test 3: Get Products
    print("\n3. Testing Products...")
    try:
        response = requests.get(f"{BASE_URL}/products/")
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ Found {len(products)} products")
            if products:
                print(f"   📦 Sample product: {products[0]['name']} - ${products[0]['price']}")
        else:
            print("   ❌ Failed to get products")
    except Exception as e:
        print(f"   ❌ Products error: {e}")
    
    # Test 4: Get Inventory
    print("\n4. Testing Inventory...")
    try:
        response = requests.get(f"{BASE_URL}/inventory/")
        if response.status_code == 200:
            inventory = response.json()
            print(f"   ✅ Found {len(inventory)} inventory records")
            
            # Check for low stock items
            low_stock_response = requests.get(f"{BASE_URL}/inventory/?low_stock_only=true")
            if low_stock_response.status_code == 200:
                low_stock = low_stock_response.json()
                print(f"   ⚠️  Low stock items: {len(low_stock)}")
        else:
            print("   ❌ Failed to get inventory")
    except Exception as e:
        print(f"   ❌ Inventory error: {e}")
    
    # Test 5: Get Sales Data
    print("\n5. Testing Sales Data...")
    try:
        response = requests.get(f"{BASE_URL}/sales/?limit=10")
        if response.status_code == 200:
            sales = response.json()
            print(f"   ✅ Found sales data (showing 10 records)")
            if sales:
                total_revenue = sum(sale['total_amount'] for sale in sales)
                print(f"   💰 Sample revenue from 10 sales: ${total_revenue:.2f}")
        else:
            print("   ❌ Failed to get sales data")
    except Exception as e:
        print(f"   ❌ Sales data error: {e}")
    
    # Test 6: Analytics - Monthly Revenue
    print("\n6. Testing Revenue Analytics...")
    try:
        # Get revenue for the last 3 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        response = requests.get(f"{BASE_URL}/analytics/revenue/monthly", params=params)
        if response.status_code == 200:
            analytics = response.json()
            print(f"   ✅ Revenue analytics for {len(analytics)} months")
            
            total_revenue = sum(period['total_revenue'] for period in analytics)
            total_sales = sum(period['total_sales'] for period in analytics)
            
            print(f"   📊 Total Revenue (3 months): ${total_revenue:.2f}")
            print(f"   📈 Total Sales Volume: {total_sales} units")
            
            if analytics:
                avg_order_value = analytics[0]['average_order_value']
                print(f"   💳 Average Order Value: ${avg_order_value:.2f}")
        else:
            print("   ❌ Failed to get revenue analytics")
    except Exception as e:
        print(f"   ❌ Revenue analytics error: {e}")
    
    # Test 7: Filter Products by Platform
    print("\n7. Testing Product Filtering...")
    try:
        response = requests.get(f"{BASE_URL}/products/?platform=Amazon")
        if response.status_code == 200:
            amazon_products = response.json()
            
            response = requests.get(f"{BASE_URL}/products/?platform=Walmart")
            walmart_products = response.json() if response.status_code == 200 else []
            
            print(f"   ✅ Amazon products: {len(amazon_products)}")
            print(f"   ✅ Walmart products: {len(walmart_products)}")
        else:
            print("   ❌ Failed to filter products")
    except Exception as e:
        print(f"   ❌ Product filtering error: {e}")
    
    # Test 8: Create New Product (if you want to test POST operations)
    print("\n8. Testing Product Creation...")
    try:
        # First get a category ID
        categories_response = requests.get(f"{BASE_URL}/categories/")
        if categories_response.status_code == 200:
            categories = categories_response.json()
            if categories:
                test_product = {
                    "name": "Test Product API",
                    "description": "A test product created via API",
                    "price": 99.99,
                    "sku": f"TEST-API-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "category_id": categories[0]['id'],
                    "platform": "Amazon",
                    "initial_stock": 100,
                    "low_stock_threshold": 20
                }
                
                response = requests.post(
                    f"{BASE_URL}/products/",
                    json=test_product,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    created_product = response.json()
                    print(f"   ✅ Created test product: {created_product['name']}")
                    print(f"   🆔 Product ID: {created_product['id']}")
                else:
                    print(f"   ❌ Failed to create product: {response.status_code}")
                    print(f"   📝 Response: {response.text}")
        else:
            print("   ⚠️  Skipping product creation (no categories found)")
    except Exception as e:
        print(f"   ❌ Product creation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Tests Completed!")
    print("\n📚 Next Steps:")
    print("   • Visit http://localhost:8000/docs for interactive API documentation")
    print("   • Use the Swagger UI to test additional endpoints")
    print("   • Check the analytics endpoints for business insights")

def test_specific_endpoints():
    """Test specific functionality with detailed output"""
    
    print("\n🔍 Detailed Endpoint Testing")
    print("=" * 50)
    
    # Test revenue analytics with different periods
    periods = ['daily', 'weekly', 'monthly']
    
    for period in periods:
        print(f"\n📊 Testing {period.upper()} revenue analytics...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            response = requests.get(f"{BASE_URL}/analytics/revenue/{period}", params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {period.capitalize()} periods found: {len(data)}")
                
                if data:
                    total_revenue = sum(p['total_revenue'] for p in data)
                    print(f"   💰 Total revenue: ${total_revenue:.2f}")
            else:
                print(f"   ❌ Failed to get {period} analytics")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 E-commerce Admin API Test Suite")
    print("🔗 Make sure the API is running at http://localhost:8000")
    print()
    
    # Run basic tests
    test_api()
    
    # Ask if user wants detailed tests
    response = input("\n❓ Run detailed analytics tests? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        test_specific_endpoints()
    
    print("\n✨ Testing complete! Check the API documentation at /docs for more details.")