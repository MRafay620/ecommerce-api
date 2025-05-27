# E-commerce Admin API

A comprehensive back-end API for powering e-commerce admin dashboards with sales analytics and inventory management capabilities.

## Features

### Core Functionality
- **Sales Analytics**: Comprehensive sales data analysis with filtering and period-based reporting
- **Revenue Analysis**: Daily, weekly, monthly, and annual revenue insights
- **Inventory Management**: Real-time inventory tracking with low stock alerts
- **Product Management**: Full CRUD operations for products and categories
- **Multi-platform Support**: Handles products from Amazon, Walmart, and other platforms

### API Capabilities
- RESTful API design with OpenAPI/Swagger documentation
- Advanced filtering and pagination
- Real-time inventory updates
- Comprehensive sales reporting
- Low stock alert system

## Technology Stack

- **Framework**: Python with FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **API Type**: RESTful
- **Documentation**: Auto-generated OpenAPI/Swagger

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/MRafay620
cd ecommerce-admin-api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
Create a PostgreSQL database:
```sql
CREATE DATABASE ecommerce_db;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO your_user;
```

### 4. Environment Configuration
Set the database URL (optional - defaults to localhost):
```bash
export DATABASE_URL="postgresql://your_user:your_password@localhost/ecommerce_db"
```

### 5. Initialize Database with Demo Data
```bash
python demo_data.py
```

### 6. Start the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Categories
- `GET /categories/` - List all categories
- `POST /categories/` - Create a new category

### Products
- `GET /products/` - List products (with filtering)
- `POST /products/` - Create a new product
- `GET /products/{product_id}` - Get specific product

### Inventory Management
- `GET /inventory/` - View inventory status
- `GET /inventory/?low_stock_only=true` - Get low stock alerts
- `PUT /inventory/{product_id}` - Update inventory levels

### Sales
- `POST /sales/` - Record a new sale
- `GET /sales/` - Get sales data (with filtering)

### Analytics
- `GET /analytics/revenue/{period}` - Revenue analysis
  - Periods: `daily`, `weekly`, `monthly`, `annual`
  - Optional filters: date range, category, platform

### Health Check
- `GET /health` - API health status

## Example API Calls

### Create a Product
```bash
curl -X POST "http://localhost:8000/products/" \
-H "Content-Type: application/json" \
-d '{
  "name": "MacBook Pro 16\"",
  "description": "Latest MacBook Pro with M3 chip",
  "price": 2499.99,
  "sku": "APL-MBP-001",
  "category_id": 1,
  "platform": "Amazon",
  "initial_stock": 50,
  "low_stock_threshold": 10
}'
```

### Get Revenue Analysis
```bash
curl "http://localhost:8000/analytics/revenue/monthly?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59"
```

### Check Low Stock Items
```bash
curl "http://localhost:8000/inventory/?low_stock_only=true"
```

### Filter Sales by Date Range
```bash
curl "http://localhost:8000/sales/?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59&limit=50"
```

## Database Schema

### Tables Overview

#### categories
- **Purpose**: Product categorization
- **Key Fields**: id, name, description, created_at
- **Relationships**: One-to-many with products

#### products
- **Purpose**: Product catalog management
- **Key Fields**: id, name, price, sku, category_id, platform, is_active
- **Relationships**: 
  - Many-to-one with categories
  - One-to-one with inventory
  - One-to-many with sales

#### inventory
- **Purpose**: Stock level tracking and low stock alerts
- **Key Fields**: id, product_id, quantity, low_stock_threshold, last_updated
- **Relationships**: One-to-one with products

#### sales
- **Purpose**: Sales transaction records
- **Key Fields**: id, product_id, quantity, unit_price, total_amount, sale_date, platform
- **Relationships**: Many-to-one with products

### Database Indexes
- **products**: name, sku, category_id
- **sales**: sale_date, product_id, platform
- **inventory**: product_id
- **categories**: name

### Key Relationships
1. **Category → Products**: One category can have multiple products
2. **Product → Inventory**: Each product has one inventory record
3. **Product → Sales**: Each product can have multiple sales records

## Demo Data

The demo data script creates:
- **8 categories** (Electronics, Home & Kitchen, Books, etc.)
- **26 sample products** from Amazon and Walmart
- **6 months of sales data** (~1,800+ sales records)
- **Inventory records** for all products
- **Low stock alerts** for testing

## Advanced Features

### Filtering Options
- **Products**: Filter by category, platform, active status
- **Sales**: Filter by date range, product, category, platform
- **Inventory**: Filter by low stock status

### Analytics Capabilities
- Revenue breakdown by time periods
- Comparison across categories and platforms
- Average order value calculations
- Sales volume analysis

### Performance Optimizations
- Database indexing on frequently queried fields
- Pagination for large datasets
- Efficient SQL queries with proper joins


## Sample Data Insights

The demo data includes:
- Products ranging from $4.99 to $599.99
- Sales across multiple platforms (Amazon, Walmart)
- Seasonal sales patterns
- Realistic inventory levels
- Low stock scenarios for testing

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database exists

2. **Import Errors**
   - Verify all requirements are installed
   - Check Python version compatibility

3. **Demo Data Issues**
   - Ensure database is empty before running demo script
   - Check database permissions

### Development Tips
- Use the interactive docs at `/docs` for testing
- Monitor logs for detailed error information
- Use database indexes for better performance with large datasets

## Future Enhancements

Potential areas for expansion:
- User authentication and authorization
- Real-time notifications for low stock
- Advanced analytics and reporting
- Integration with external e-commerce platforms
- Caching layer for improved performance
- GraphQL endpoint for complex queries
