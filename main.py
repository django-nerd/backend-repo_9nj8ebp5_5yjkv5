import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from database import db, create_document
from schemas import Order

app = FastAPI(title="SurpriseSoul API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SurpriseSoul API running"}

# Utilities

def to_serializable(doc):
    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if k == "_id":
                out[k] = str(v)
            elif isinstance(v, list):
                out[k] = [to_serializable(i) for i in v]
            elif isinstance(v, dict):
                out[k] = to_serializable(v)
            else:
                out[k] = v
        return out
    return doc

# Seed some showcase products if none exist
@app.post("/seed")
def seed_products():
    if db is None:
        # If database isn't configured, just no-op so frontend still works
        return {"seeded": False, "message": "Database not configured"}

    existing = db["product"].count_documents({})
    if existing > 0:
        return {"seeded": False, "message": "Products already exist"}

    sample_products: List[dict] = [
        {
            "title": "3D Printed Diamond Cut LED Frame",
            "slug": "3d-printed-diamond-cut-led-frame",
            "description": "A premium 3D printed LED frame with diamond-cut edges that glows softly, turning your photos into luminous art.",
            "price": 2499,
            "discount_percent": 20,
            "rating": 4.9,
            "images": [
                "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?q=80&w=1200&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1600347020011-8b88c43eaecf?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["Best Seller", "Handmade"],
            "variants": [
                {"name": "Size", "options": ["Small", "Medium", "Large"]},
                {"name": "Light Color", "options": ["Warm", "Cool", "RGB"]}
            ],
            "featured": True,
            "category": "frames"
        },
        {
            "title": "Personalized Wooden Photo Frame with LED",
            "slug": "personalized-wooden-led-frame",
            "description": "Elegant wooden frame with embedded warm LEDs, personalized with name and message.",
            "price": 1999,
            "discount_percent": 15,
            "rating": 4.8,
            "images": [
                "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["Free Personalization"],
            "variants": [
                {"name": "Size", "options": ["8x8", "10x10", "12x12"]},
                {"name": "Light Color", "options": ["Warm", "Cool"]}
            ],
            "featured": True,
            "category": "frames"
        },
        {
            "title": "Crystal Acrylic Night Lamp",
            "slug": "crystal-acrylic-night-lamp",
            "description": "Acrylic panel etched with your photo and message, illuminated by soft LEDs.",
            "price": 1599,
            "discount_percent": 10,
            "rating": 4.7,
            "images": [
                "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["New"],
            "variants": [
                {"name": "Size", "options": ["Small", "Medium"]}
            ],
            "featured": False,
            "category": "lamps"
        }
    ]

    for p in sample_products:
        db["product"].insert_one(p)

    return {"seeded": True, "count": len(sample_products)}

@app.get("/products")
def list_products():
    if db is None:
        # fallback demo products when DB is not available
        return [
            {
                "_id": "demo1",
                "title": "3D Printed Diamond Cut LED Frame",
                "slug": "3d-printed-diamond-cut-led-frame",
                "price": 2499,
                "discount_percent": 20,
                "rating": 4.9,
                "images": ["https://images.unsplash.com/photo-1542038784456-1ea8e935640e?q=80&w=1200&auto=format&fit=crop"],
                "badges": ["Best Seller", "Handmade"],
                "variants": [
                    {"name": "Size", "options": ["Small", "Medium", "Large"]},
                    {"name": "Light Color", "options": ["Warm", "Cool", "RGB"]}
                ]
            },
            {
                "_id": "demo2",
                "title": "Personalized Wooden Photo Frame with LED",
                "slug": "personalized-wooden-led-frame",
                "price": 1999,
                "discount_percent": 15,
                "rating": 4.8,
                "images": ["https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop"],
                "badges": ["Free Personalization"],
                "variants": [
                    {"name": "Size", "options": ["8x8", "10x10", "12x12"]},
                    {"name": "Light Color", "options": ["Warm", "Cool"]}
                ]
            },
            {
                "_id": "demo3",
                "title": "Crystal Acrylic Night Lamp",
                "slug": "crystal-acrylic-night-lamp",
                "price": 1599,
                "discount_percent": 10,
                "rating": 4.7,
                "images": ["https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop"],
                "badges": ["New"],
                "variants": [{"name": "Size", "options": ["Small", "Medium"]}]
            }
        ]
    products = list(db["product"].find({}).limit(24))
    return [to_serializable(p) for p in products]

@app.get("/products/{slug}")
def get_product(slug: str):
    if db is None:
        demo = next((p for p in list_products() if p["slug"] == slug), None)
        if not demo:
            raise HTTPException(status_code=404, detail="Product not found")
        return demo
    p = db["product"].find_one({"slug": slug})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_serializable(p)

@app.post("/orders")
def create_order(order: Order):
    if db is None:
        # accept orders even without DB for demo
        return {"order_id": "demo-order"}
    order_id = create_document("order", order)
    return {"order_id": order_id}

@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    return {"url": f"/uploads/{file.filename}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
