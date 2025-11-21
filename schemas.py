"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal

class ProductVariant(BaseModel):
    name: str = Field(..., description="Variant name, e.g., Size")
    options: List[str] = Field(..., description="Available options for this variant")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="Unique slug for routing")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Base price in INR")
    discount_percent: Optional[int] = Field(0, ge=0, le=90)
    rating: float = Field(4.8, ge=0, le=5)
    images: List[str] = Field(default_factory=list, description="Image URLs")
    badges: List[str] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    featured: bool = Field(False)
    category: str = Field("frames")

class Personalization(BaseModel):
    photo_url: Optional[str] = None
    name: Optional[str] = None
    message: Optional[str] = None
    size: Optional[str] = None
    light_color: Optional[str] = None

class OrderItem(BaseModel):
    product_slug: str
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., ge=0)
    personalization: Optional[Personalization] = None

class CustomerInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None

class Order(BaseModel):
    items: List[OrderItem]
    subtotal: float
    discount: float = 0
    shipping: float = 0
    total: float
    payment_method: Literal["COD", "Prepaid"] = "COD"
    customer: Optional[CustomerInfo] = None
    status: Literal["pending", "confirmed", "shipped", "delivered"] = "pending"
