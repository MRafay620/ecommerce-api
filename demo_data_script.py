import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Category, Product, Inventory, Sale

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:rafay@localhost/ecommerce_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_demo_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Sale).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()
        
        print("Creating categories...")
        
        # Create Categories
        categories = [
            Category(name="Electronics", description="Electronic devices and accessories"),
            Category(name="Home & Kitchen", description="Home appliances and kitchen items"),
            Category(name="Books", description="Books and educational materials"),
            Category(name="Clothing", description="Apparel and fashion items"),
            Category(name="Sports & Outdoors", description="Sports equipment and outdoor gear"),
            Category(name="Beauty & Personal Care", description="Beauty products and personal care items"),
            Category(name="Toys & Games", description="Toys and gaming products"),
            Category(name="Health & Household", description="Health products and household items")
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        
        print("Creating products...")
        
        # Sample products for Amazon and Walmart
        products_data = [
            # Electronics
            {"name": "Samsung Galaxy Earbuds Pro", "price": 199.99, "sku": "SAM-EAR-001", "category": "Electronics", "platform": "Amazon"},
            {"name": "iPhone 15 Case", "price": 24.99, "sku": "APL-CAS-001", "category": "Electronics", "platform": "Amazon"},
            {"name": "Sony WH-1000XM4 Headphones", "price": 349.99, "sku": "SON-HEA-001", "category": "Electronics", "platform": "Walmart"},
            {"name": "Anker PowerBank 10000mAh", "price": 45.99, "sku": "ANK-POW-001", "category": "Electronics", "platform": "Amazon"},
            {"name": "Logitech MX Master 3 Mouse", "price": 99.99, "sku": "LOG-MOU-001", "category": "Electronics", "platform": "Walmart"},
            
            # Home & Kitchen
            {"name": "Instant Pot Duo 7-in-1", "price": 89.99, "sku": "INS-POT-001", "category": "Home & Kitchen", "platform": "Amazon"},
            {"name": "KitchenAid Stand Mixer", "price": 399.99, "sku": "KIT-MIX-001", "category": "Home & Kitchen", "platform": "Walmart"},
            {"name": "Ninja Blender", "price": 79.99, "sku": "NIN-BLE-001", "category": "Home & Kitchen", "platform": "Amazon"},
            {"name": "Dyson V11 Vacuum", "price": 599.99, "sku": "DYS-VAC-001", "category": "Home & Kitchen", "platform": "Walmart"},
            
            # Books
            {"name": "The Psychology of Money", "price": 16.99, "sku": "BOO-PSY-001", "category": "Books", "platform": "Amazon"},
            {"name": "Atomic Habits", "price": 18.99, "sku": "BOO-HAB-001", "category": "Books", "platform": "Amazon"},
            {"name": "The 7 Habits of Highly Effective People", "price": 15.99, "sku": "BOO-HAB-002", "category": "Books", "platform": "Walmart"},
            
            # Clothing
            {"name": "Nike Air Max 270", "price": 129.99, "sku": "NIK-SHO-001", "category": "Clothing", "platform": "Amazon"},
            {"name": "Levi's 501 Original Jeans", "price": 69.99, "sku": "LEV-JEA-001", "category": "Clothing", "platform": "Walmart"},
            {"name": "Adidas Ultraboost 22", "price": 179.99, "sku": "ADI-SHO-001", "category": "Clothing", "platform": "Amazon"},
            
            # Sports & Outdoors
            {"name": "Yeti Rambler 30oz", "price": 39.99, "sku": "YET-RAM-001", "category": "Sports & Outdoors", "platform": "Amazon"},
            {"name": "Coleman 4-Person Tent", "price": 119.99, "sku": "COL-TEN-001", "category": "Sports & Outdoors", "platform": "Walmart"},
            {"name": "Hydro Flask Water Bottle", "price": 44.99, "sku": "HYD-BOT-001", "category": "Sports & Outdoors", "platform": "Amazon"},
            
            # Beauty & Personal Care
            {"name": "CeraVe Moisturizing Cream", "price": 19.99, "sku": "CER-MOI-001", "category": "Beauty & Personal Care", "platform": "Amazon"},
            {"name": "Olay Regenerist Serum", "price": 28.99, "sku": "OLA-SER-001", "category": "Beauty & Personal Care", "platform": "Walmart"},
            {"name": "Neutrogena Sunscreen SPF 50", "price": 12.99, "sku": "NEU-SUN-001", "category": "Beauty & Personal Care", "platform": "Amazon"},
            
            # Toys & Games
            {"name": "LEGO Creator 3-in-1 Deep Sea Creatures", "price": 79.99, "sku": "LEG-CRE-001", "category": "Toys & Games", "platform": "Amazon"},
            {"name": "Monopoly Classic Board Game", "price": 24.99, "sku": "MON-CLA-001", "category": "Toys & Games", "platform": "Walmart"},
            {"name": "Hot Wheels 20-Car Pack", "price": 19.99, "sku": "HOT-CAR-001", "category": "Toys & Games", "platform": "Amazon"},
            
            # Health & Household
            {"name": "Charmin Ultra Soft Toilet Paper", "price": 24.99, "sku": "CHA-TOI-001", "category": "Health & Household", "platform": "Walmart"},
            {"name": "Tide Laundry Detergent Pods", "price": 18.99, "sku": "TID-DET-001", "category": "Health & Household", "platform": "Amazon"},
            {"name": "Lysol Disinfecting Wipes", "price": 4.99, "sku": "LYS-WIP-001", "category": "Health & Household", "platform": "Walmart"}
        ]
        
        # Create Products with Inventory
        created_products = []
        for product_data in products_data:
            category = db.query(Category).filter(Category.name == product_data["category"]).first()
            
            product = Product(
                name=product_data["name"],
                description=f"High-quality {product_data['name']} available on {product_data['platform']}",
                price=product_data["price"],
                sku=product_data["sku"],
                category_id=category.id,
                platform=product_data["platform"],
                is_active=True
            )
            
            db.add(product)
            created_products.append(product)
        
        db.commit()
        
        print("Creating inventory records...")
        
        # Create Inventory for each product
        for product in created_products:
            inventory = Inventory(
                product_id=product.id,
                quantity=random.randint(5, 500),
                low_stock_threshold=random.randint(10, 50)
            )
            db.add(inventory)
        
        db.commit()
        
        print("Creating sales data...")
        
        # Create Sales Data (last 6 months)
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now()
        
        sales_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 5-20 sales per day
            daily_sales = random.randint(5, 20)
            
            for _ in range(daily_sales):
                product = random.choice(created_products)
                quantity = random.randint(1, 5)
                
                # Add some price variation (±10%)
                price_variation = random.uniform(0.9, 1.1)
                unit_price = round(product.price * price_variation, 2)
                
                # Random time during the day
                sale_time = current_date + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                sale = Sale(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=quantity * unit_price,
                    sale_date=sale_time,
                    platform=product.platform,
                    order_id=f"ORD-{random.randint(100000, 999999)}"
                )
                
                sales_data.append(sale)
            
            current_date += timedelta(days=1)
        
        # Batch insert sales
        db.add_all(sales_data)
        db.commit()
        
        print(f"Demo data created successfully!")
        print(f"- Categories: {len(categories)}")
        print(f"- Products: {len(created_products)}")
        print(f"- Sales records: {len(sales_data)}")
        
        # Create some low stock items for testing
        low_stock_products = random.sample(created_products, 5)
        for product in low_stock_products:
            inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
            if inventory:
                inventory.quantity = random.randint(1, 9)  # Below typical threshold
        
        db.commit()
        print("- Low stock alerts created for testing")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()