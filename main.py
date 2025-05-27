from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import os
from enum import Enum

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ecommerce_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # Amazon, Walmart, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    sales = relationship("Sale", back_populates="product")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="inventory")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    order_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="sales")

# Pydantic Models
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    category_id: int
    platform: str
    initial_stock: Optional[int] = 0
    low_stock_threshold: Optional[int] = 10

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    sku: str
    category_id: int
    platform: str
    is_active: bool
    created_at: datetime
    category: CategoryResponse
    
    class Config:
        from_attributes = True

class InventoryUpdate(BaseModel):
    quantity: int
    low_stock_threshold: Optional[int] = None

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    low_stock_threshold: int
    last_updated: datetime
    is_low_stock: bool
    product: ProductResponse
    
    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    sale_date: datetime
    platform: str
    order_id: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    sale_date: datetime
    platform: str
    order_id: Optional[str]
    product: ProductResponse
    
    class Config:
        from_attributes = True

class RevenueAnalysis(BaseModel):
    period: str
    total_revenue: float
    total_sales: int
    average_order_value: float
    start_date: datetime
    end_date: datetime

class PeriodType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    annual = "annual"

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI App
app = FastAPI(
    title="E-commerce Admin API",
    description="API for e-commerce admin dashboard with sales analytics and inventory management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# API Endpoints

# Categories
@app.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# Products
@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Create product
    product_data = product.dict()
    initial_stock = product_data.pop('initial_stock', 0)
    low_stock_threshold = product_data.pop('low_stock_threshold', 10)
    
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create initial inventory
    db_inventory = Inventory(
        product_id=db_product.id,
        quantity=initial_stock,
        low_stock_threshold=low_stock_threshold
    )
    db.add(db_inventory)
    db.commit()
    
    return db_product

@app.get("/products/", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if platform:
        query = query.filter(Product.platform == platform)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    return query.all()

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Inventory Management
@app.get("/inventory/", response_model=List[InventoryResponse])
def get_inventory(
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Inventory).join(Product)
    
    if low_stock_only:
        query = query.filter(Inventory.quantity <= Inventory.low_stock_threshold)
    
    inventories = query.all()
    
    # Add is_low_stock field
    for inventory in inventories:
        inventory.is_low_stock = inventory.quantity <= inventory.low_stock_threshold
    
    return inventories

@app.put("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.quantity = inventory_update.quantity
    if inventory_update.low_stock_threshold is not None:
        inventory.low_stock_threshold = inventory_update.low_stock_threshold
    
    db.commit()
    db.refresh(inventory)
    inventory.is_low_stock = inventory.quantity <= inventory.low_stock_threshold
    
    return inventory

# Sales
@app.post("/sales/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate total amount
    total_amount = sale.quantity * sale.unit_price
    
    # Create sale
    db_sale = Sale(
        product_id=sale.product_id,
        quantity=sale.quantity,
        unit_price=sale.unit_price,
        total_amount=total_amount,
        sale_date=sale.sale_date,
        platform=sale.platform,
        order_id=sale.order_id
    )
    
    db.add(db_sale)
    
    # Update inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == sale.product_id).first()
    if inventory:
        inventory.quantity -= sale.quantity
        if inventory.quantity < 0:
            inventory.quantity = 0
    
    db.commit()
    db.refresh(db_sale)
    
    return db_sale

@app.get("/sales/", response_model=List[SaleResponse])
def get_sales(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Sale).join(Product)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if platform:
        query = query.filter(Sale.platform == platform)
    
    return query.order_by(Sale.sale_date.desc()).offset(offset).limit(limit).all()

# Revenue Analysis
@app.get("/analytics/revenue/{period}", response_model=List[RevenueAnalysis])
def get_revenue_analysis(
    period: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    query = db.query(Sale).join(Product)
    query = query.filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if platform:
        query = query.filter(Sale.platform == platform)
    
    sales = query.all()
    
    # Group sales by period
    grouped_sales = {}
    
    for sale in sales:
        if period == PeriodType.daily:
            key = sale.sale_date.date()
        elif period == PeriodType.weekly:
            key = sale.sale_date.date() - timedelta(days=sale.sale_date.weekday())
        elif period == PeriodType.monthly:
            key = sale.sale_date.replace(day=1).date()
        else:  # annual
            key = sale.sale_date.replace(month=1, day=1).date()
        
        if key not in grouped_sales:
            grouped_sales[key] = {
                'total_revenue': 0,
                'total_sales': 0,
                'sales_count': 0
            }
        
        grouped_sales[key]['total_revenue'] += sale.total_amount
        grouped_sales[key]['total_sales'] += sale.quantity
        grouped_sales[key]['sales_count'] += 1
    
    # Convert to response format
    result = []
    for date_key, data in grouped_sales.items():
        avg_order_value = data['total_revenue'] / data['sales_count'] if data['sales_count'] > 0 else 0
        
        if period == PeriodType.daily:
            period_end = datetime.combine(date_key, datetime.min.time()) + timedelta(days=1) - timedelta(seconds=1)
        elif period == PeriodType.weekly:
            period_end = datetime.combine(date_key, datetime.min.time()) + timedelta(days=7) - timedelta(seconds=1)
        elif period == PeriodType.monthly:
            next_month = date_key.replace(day=28) + timedelta(days=4)
            period_end = (next_month - timedelta(days=next_month.day)).replace(hour=23, minute=59, second=59)
        else:  # annual
            period_end = date_key.replace(year=date_key.year + 1) - timedelta(seconds=1)
        
        result.append(RevenueAnalysis(
            period=period.value,
            total_revenue=data['total_revenue'],
            total_sales=data['total_sales'],
            average_order_value=avg_order_value,
            start_date=datetime.combine(date_key, datetime.min.time()),
            end_date=period_end
        ))
    
    return sorted(result, key=lambda x: x.start_date)

# Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)