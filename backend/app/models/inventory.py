
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base

class MedicineProduct(Base):
    __tablename__ = "medicine_products"
    id               = Column(Integer, primary_key=True, index=True)
    name             = Column(String, index=True)
    category         = Column(String, index=True)
    sub_category     = Column(String)
    price            = Column(Float)
    manufacturer     = Column(String)
    salt_composition = Column(String)

class InventoryRecord(Base):
    __tablename__ = "inventory_records"
    id                = Column(Integer, primary_key=True, index=True)
    region            = Column(String, index=True)
    district          = Column(String, index=True)
    medicine_category = Column(String, index=True)
    medicine_name     = Column(String)
    date              = Column(String)
    month             = Column(Integer)
    year              = Column(Integer)
    season            = Column(String)
    weather           = Column(String)
    disease           = Column(String)
    demand            = Column(Integer)
    stock             = Column(Integer)
    sales             = Column(Integer)
    stockout          = Column(Integer, default=0)
    reorder_qty       = Column(Integer, default=0)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

class RegionSalesRecord(Base):
    __tablename__ = "region_sales"
    id                = Column(Integer, primary_key=True, index=True)
    region            = Column(String, index=True)
    district          = Column(String)
    year              = Column(Integer)
    month             = Column(Integer)
    season            = Column(String)
    weather           = Column(String)
    top_disease       = Column(String)
    medicine_category = Column(String)
    total_demand      = Column(Integer)
    total_sales       = Column(Integer)
    total_stock       = Column(Integer)
    avg_stockout      = Column(Float)

class QTableRecord(Base):
    __tablename__ = "qtable_records"
    id                = Column(Integer, primary_key=True, index=True)
    region            = Column(String)
    district          = Column(String)
    medicine_category = Column(String)
    q_table           = Column(JSON)
    episodes          = Column(Integer)
    total_reward      = Column(Float)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
