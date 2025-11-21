import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

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

# -----------------------------
# Demo catalog (fallback when DB missing)
# -----------------------------

def demo_catalog() -> List[Dict[str, Any]]:
    return [
        {
            "_id": "demo1",
            "title": "3D Printed Diamond Cut LED Frame",
            "slug": "3d-printed-diamond-cut-led-frame",
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
            "category": "3d-led-frames",
        },
        {
            "_id": "demo2",
            "title": "Personalized Wooden LED Frame",
            "slug": "personalized-wooden-led-frame",
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
            "category": "wooden-frames",
        },
        {
            "_id": "demo3",
            "title": "Crystal Acrylic Night Lamp",
            "slug": "crystal-acrylic-night-lamp",
            "price": 1599,
            "discount_percent": 10,
            "rating": 4.7,
            "images": [
                "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["New"],
            "variants": [{"name": "Size", "options": ["Small", "Medium"]}],
            "category": "lamps",
        },
        {
            "_id": "demo4",
            "title": "Spotify Music Plaque with Stand",
            "slug": "spotify-music-plaque",
            "price": 1299,
            "discount_percent": 10,
            "rating": 4.8,
            "images": [
                "https://images.unsplash.com/photo-1526318472351-c75fcf070305?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["Trending"],
            "variants": [
                {"name": "Size", "options": ["A5", "A4"]}
            ],
            "category": "plaques",
        },
        {
            "_id": "demo5",
            "title": "Couple Photo Collage Frame",
            "slug": "couple-photo-collage-frame",
            "price": 1799,
            "discount_percent": 12,
            "rating": 4.6,
            "images": [
                "https://images.unsplash.com/photo-1489367874814-f5d040621dd8?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["Anniversary Special"],
            "variants": [
                {"name": "Size", "options": ["12x12", "16x16"]}
            ],
            "category": "collage",
        },
        {
            "_id": "demo6",
            "title": "Engraved Wooden Nameplate",
            "slug": "engraved-wooden-nameplate",
            "price": 999,
            "discount_percent": 5,
            "rating": 4.5,
            "images": [
                "https://images.unsplash.com/photo-1545235617-9465d2a55698?q=80&w=1200&auto=format&fit=crop"
            ],
            "badges": ["Personalized"],
            "variants": [
                {"name": "Finish", "options": ["Natural", "Walnut"]}
            ],
            "category": "nameplates",
        },
    ]


def demo_product_detail(slug: str) -> Dict[str, Any]:
    base = next((p for p in demo_catalog() if p["slug"] == slug), None)
    if not base:
        return None
    # Rich, tabbed content similar to the reference site
    details = {
        "3d-printed-diamond-cut-led-frame": {
            "description": "Premium diamond-cut 3D printed LED frame that turns your photo into luminous art. Perfect for birthdays, anniversaries and room decor.",
            "features": [
                "Diamond-cut 3D printed bezel",
                "Soft, power-efficient LEDs",
                "Handcrafted finish",
                "Free personalization (name & message)",
            ],
            "specs": [
                {"label": "Material", "value": "PLA + Acrylic front"},
                {"label": "Light", "value": "Warm / Cool / RGB"},
                {"label": "Power", "value": "USB 5V"},
                {"label": "Sizes", "value": "Small / Medium / Large"},
            ],
            "whats_in_box": ["LED frame", "USB cable", "Personalized print", "Care card"],
            "care": ["Wipe with dry cloth", "Keep away from direct sunlight", "Do not wash"],
            "faqs": [
                {"q": "How long does delivery take?", "a": "Most orders dispatch in 24-48 hours and deliver within 3-6 days."},
                {"q": "Can I Cash on Delivery?", "a": "Yes, COD available in most pincodes."},
                {"q": "What photo works best?", "a": "High-resolution, bright photos give the best result."}
            ],
            "shipping": "Free shipping across India. Return/replacement for transit damage only.",
            "how_to_order": [
                "Choose size and light colour",
                "Upload your photo & add names/message",
                "Add to cart and place order (COD available)",
            ],
        },
        "personalized-wooden-led-frame": {
            "description": "Elegant wooden frame with warm LEDs and your custom text.",
            "features": ["Premium wood finish", "Warm LED glow", "Free engraving"],
            "specs": [
                {"label": "Material", "value": "Engineered wood + Acrylic"},
                {"label": "Sizes", "value": "8x8 / 10x10 / 12x12"},
            ],
            "whats_in_box": ["Frame", "USB cable"],
            "care": ["Dry cloth only"],
            "faqs": [
                {"q": "Is wall mounting included?", "a": "Table stand included, wall hooks optional."}
            ],
            "shipping": "Ships free. 3-6 days delivery.",
            "how_to_order": ["Select size", "Add text", "Checkout"],
        },
        "crystal-acrylic-night-lamp": {
            "description": "Crystal-style acrylic night lamp etched with your photo.",
            "features": ["Laser etched acrylic", "Ambient light"],
            "specs": [
                {"label": "Sizes", "value": "Small / Medium"}
            ],
            "whats_in_box": ["Lamp base", "Acrylic plate", "USB cable"],
            "care": ["Handle acrylic with care"],
            "faqs": [],
            "shipping": "Standard shipping 3-6 days",
            "how_to_order": ["Upload photo", "Add to cart", "Place order"],
        },
        "spotify-music-plaque": {
            "description": "Personalized Spotify code plaque with stand.",
            "features": ["Scan to play", "High-clarity acrylic"],
            "specs": [{"label": "Size", "value": "A5 / A4"}],
            "whats_in_box": ["Plaque", "Stand"],
            "care": ["Avoid scratches"],
            "faqs": [],
            "shipping": "Ships in 24-48h",
            "how_to_order": ["Share song link", "Choose size", "Checkout"],
        },
        "couple-photo-collage-frame": {
            "description": "Romantic collage frame for couples.",
            "features": ["Multiple photo layout", "Gift-ready packaging"],
            "specs": [{"label": "Sizes", "value": "12x12 / 16x16"}],
            "whats_in_box": ["Frame", "Hanging kit"],
            "care": ["Wipe clean"],
            "faqs": [],
            "shipping": "Free shipping",
            "how_to_order": ["Upload photos", "Confirm layout", "Place order"],
        },
        "engraved-wooden-nameplate": {
            "description": "Custom engraved wooden nameplate.",
            "features": ["Laser engraving", "Premium finishes"],
            "specs": [{"label": "Finish", "value": "Natural / Walnut"}],
            "whats_in_box": ["Nameplate", "Mounting tape"],
            "care": ["Keep dry"],
            "faqs": [],
            "shipping": "Ships in 2-3 days",
            "how_to_order": ["Enter names", "Choose finish", "Checkout"],
        },
    }
    extra = details.get(slug, {})
    return {**base, **extra}


# -----------------------------
# Seed some showcase products if DB exists
# -----------------------------
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
            "category": "3d-led-frames",
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
            "category": "wooden-frames",
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
            "category": "lamps",
        }
    ]

    for p in sample_products:
        db["product"].insert_one(p)

    return {"seeded": True, "count": len(sample_products)}


@app.get("/products")
def list_products():
    if db is None:
        # fallback demo products when DB is not available
        return demo_catalog()
    products = list(db["product"].find({}).limit(48))
    return [to_serializable(p) for p in products]


@app.get("/products/{slug}")
def get_product(slug: str):
    if db is None:
        demo = demo_product_detail(slug)
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
    # In demo, we don't persist the file; return a pretend URL so the UI can proceed
    return {"url": f"/uploads/{file.filename}"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
