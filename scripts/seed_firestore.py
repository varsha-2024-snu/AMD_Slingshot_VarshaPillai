"""
seed_firestore.py — One-shot script to populate the ShopGenie product catalog.

Run once before the demo. Safe to re-run — uses set() with merge=False to overwrite.
Generates 50 products across 5 categories with realistic INR pricing and GCS image URL stubs.

Usage:
    python scripts/seed_firestore.py
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# Initialise Firebase Admin for the seeding script
if not firebase_admin._apps:
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    if not project_id:
        print("❌ FIREBASE_PROJECT_ID environment variable is not set.")
        sys.exit(1)
        
    cred = None
    if os.path.exists("service-account.json"):
        cred = credentials.Certificate("service-account.json")
        
    firebase_admin.initialize_app(
        credential=cred,
        options={"projectId": project_id}
    )

db = firestore.client()

GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "shopgenie-images")

PRODUCTS = [
    # --- TOYS (10 products) ---
    {"name": "Dinosaur Discovery Set", "description": "12-piece realistic dinosaur figurines with a fossil excavation kit. Includes T-Rex, Triceratops, and Brachiosaurus. Educational booklet included.", "category": "toys", "price": 749.0, "tags": ["dinosaur", "educational", "age-8-12", "stem", "figurine"], "stock": 45},
    {"name": "Magnetic Building Tiles (64-piece)", "description": "STEM magnetic construction tiles in 8 vivid colours. Build bridges, towers, and geometric shapes. Safe for ages 3+.", "category": "toys", "price": 1299.0, "tags": ["stem", "magnetic", "building", "age-3-plus", "educational"], "stock": 30},
    {"name": "Junior Chess Set", "description": "Lightweight wooden chess set with illustrated instruction booklet for beginners. Board folds for storage.", "category": "toys", "price": 549.0, "tags": ["chess", "board-game", "strategy", "age-6-plus", "wooden"], "stock": 60},
    {"name": "Remote Control Excavator", "description": "Full-function RC construction excavator with working bucket arm. USB rechargeable. Suitable for ages 6+.", "category": "toys", "price": 1849.0, "tags": ["remote-control", "construction", "excavator", "age-6-plus", "rc"], "stock": 20},
    {"name": "Glow-in-the-Dark Star Projector", "description": "Bedroom ceiling star projector with 8 colour modes and sleep timer. Doubles as a nightlight.", "category": "toys", "price": 899.0, "tags": ["projector", "stars", "bedroom", "nightlight", "age-5-plus"], "stock": 35},
    {"name": "Slime Science Lab Kit", "description": "Make 10 types of slime at home. Non-toxic, washable formula. Includes glitter, glow-in-dark powder, and magnetic beads.", "category": "toys", "price": 649.0, "tags": ["slime", "science", "diy", "age-6-plus", "non-toxic"], "stock": 50},
    {"name": "Dinosaur Egg Surprise (set of 3)", "description": "Grow your own dinosaur — submerge in water and the egg hatches over 72 hours. Assorted species.", "category": "toys", "price": 349.0, "tags": ["dinosaur", "surprise", "grow", "age-4-plus", "hatching"], "stock": 80},
    {"name": "Coding Robot for Kids", "description": "Beginner-friendly programmable robot that teaches block-based coding logic. Works with free iOS and Android app.", "category": "toys", "price": 2499.0, "tags": ["coding", "robot", "stem", "educational", "age-6-plus"], "stock": 15},
    {"name": "Wooden Puzzle World Map (100 pieces)", "description": "Illustrated world map jigsaw with country names. Finished size 60×40cm. Age 6+.", "category": "toys", "price": 499.0, "tags": ["puzzle", "map", "educational", "wooden", "age-6-plus"], "stock": 40},
    {"name": "Kinetic Sand Art Studio", "description": "1kg of kinetic sand with 10 moulds and sculpting tools. Mess-free creative play. Age 3+.", "category": "toys", "price": 799.0, "tags": ["sand", "creative", "sensory", "age-3-plus", "art"], "stock": 55},

    # --- ELECTRONICS (10 products) ---
    {"name": "Noise-Cancelling Study Headphones", "description": "Over-ear headphones with active noise cancellation. 30hr battery life. Foldable for commuting. Black.", "category": "electronics", "price": 2999.0, "tags": ["headphones", "noise-cancelling", "study", "over-ear", "wireless"], "stock": 25},
    {"name": "Smart LED Desk Lamp", "description": "Touch-dimmer desk lamp with 5 colour temperatures. USB-A charging port on base. Eye-care flicker-free.", "category": "electronics", "price": 1499.0, "tags": ["lamp", "led", "desk", "usb", "eye-care", "smart"], "stock": 40},
    {"name": "Portable Bluetooth Speaker (Waterproof)", "description": "360-degree sound, IPX7 waterproof, 12hr playtime. Connects 2 speakers for stereo. Available in 4 colours.", "category": "electronics", "price": 1799.0, "tags": ["speaker", "bluetooth", "waterproof", "portable", "outdoor"], "stock": 30},
    {"name": "USB-C 65W GaN Charger", "description": "Compact 3-port GaN charger (2×USB-C + 1×USB-A). Charges laptop, phone, and tablet simultaneously. Travel-friendly.", "category": "electronics", "price": 1299.0, "tags": ["charger", "usb-c", "gan", "65w", "travel", "fast-charge"], "stock": 60},
    {"name": "Wireless Ergonomic Mouse", "description": "Vertical ergonomic design reduces wrist strain. 2.4GHz wireless, 90-day battery. Works on all surfaces.", "category": "electronics", "price": 999.0, "tags": ["mouse", "ergonomic", "wireless", "wrist", "office"], "stock": 45},
    {"name": "Mini Thermal Printer", "description": "Pocket-sized Bluetooth thermal printer. Prints photos, labels, and notes on BPA-free paper. App-controlled.", "category": "electronics", "price": 2299.0, "tags": ["printer", "thermal", "bluetooth", "portable", "pocket"], "stock": 20},
    {"name": "Smart Plug (Wi-Fi, 2-pack)", "description": "Schedule and remote-control any appliance via app. Works with Alexa and Google Home. Energy monitoring.", "category": "electronics", "price": 899.0, "tags": ["smart-plug", "wifi", "alexa", "google-home", "energy"], "stock": 70},
    {"name": "Webcam 1080p with Ring Light", "description": "Full HD webcam with built-in soft ring light and noise-cancelling microphone. Plug-and-play USB-A.", "category": "electronics", "price": 1999.0, "tags": ["webcam", "1080p", "ring-light", "microphone", "work-from-home"], "stock": 35},
    {"name": "Digital Luggage Scale", "description": "Backlit LCD, reads in kg/lb, 50kg capacity. Compact for travel. Includes lanyard.", "category": "electronics", "price": 349.0, "tags": ["scale", "luggage", "travel", "digital", "compact"], "stock": 90},
    {"name": "Solar Power Bank 20000mAh", "description": "Dual solar panels + USB-C + USB-A output. LED flashlight. Ideal for travel and power cuts.", "category": "electronics", "price": 1899.0, "tags": ["power-bank", "solar", "20000mah", "travel", "outdoor", "eco-friendly"], "stock": 25},

    # --- CLOTHING (10 products) ---
    {"name": "Merino Wool Blend Scarf", "description": "Ultra-soft 70% merino, 30% acrylic blend. 200×30cm. Machine washable. 8 neutral colours.", "category": "clothing", "price": 799.0, "tags": ["scarf", "merino", "wool", "winter", "sustainable", "soft"], "stock": 50},
    {"name": "Organic Cotton Unisex Hoodie", "description": "100% GOTS-certified organic cotton. Kangaroo pocket. Preshrunk. Available sizes XS–3XL.", "category": "clothing", "price": 1599.0, "tags": ["hoodie", "organic", "cotton", "sustainable", "unisex", "eco-friendly"], "stock": 40},
    {"name": "Compression Running Socks (3-pack)", "description": "Graduated compression for better circulation. Moisture-wicking. Sizes S/M/L. Arch support panel.", "category": "clothing", "price": 499.0, "tags": ["socks", "compression", "running", "sport", "moisture-wicking"], "stock": 100},
    {"name": "Lightweight Packable Rain Jacket", "description": "Packs into its own pocket. Waterproof, windproof. Mesh lining. Available in 6 colours. Sizes XS–XXL.", "category": "clothing", "price": 2499.0, "tags": ["jacket", "rain", "packable", "waterproof", "travel", "outdoor"], "stock": 30},
    {"name": "Adaptive Easy-Dress Shirt (Disability-Aid)", "description": "Magnetic snap closures disguised as buttons. Wide armholes for wheelchair users. Wrinkle-resistant. Formal look.", "category": "clothing", "price": 1299.0, "tags": ["adaptive", "disability-aid", "shirt", "magnetic", "accessible", "formal"], "stock": 20},
    {"name": "Kids Organic Pyjama Set", "description": "100% organic cotton. Long-sleeve top + full-length bottoms. Anti-pill fabric. Age 3–12.", "category": "clothing", "price": 699.0, "tags": ["pyjamas", "kids", "organic", "cotton", "sleepwear", "age-3-12"], "stock": 60},
    {"name": "Thermal Base Layer Set", "description": "Brushed fleece inner lining. Top + bottoms. Flatlock seams prevent chafing. Sizes S–XXL.", "category": "clothing", "price": 1199.0, "tags": ["thermal", "base-layer", "winter", "fleece", "sport"], "stock": 35},
    {"name": "Bamboo Sports T-Shirt", "description": "70% bamboo, 30% recycled polyester. Naturally antibacterial, odour-resistant. Slim fit. 6 colours.", "category": "clothing", "price": 799.0, "tags": ["t-shirt", "bamboo", "eco-friendly", "sport", "antibacterial", "sustainable"], "stock": 55},
    {"name": "Fleece-Lined Waterproof Gloves", "description": "Touchscreen-compatible fingertips. Adjustable wrist strap. Sizes S/M/L/XL.", "category": "clothing", "price": 599.0, "tags": ["gloves", "fleece", "waterproof", "touchscreen", "winter"], "stock": 45},
    {"name": "Wide-Fit Diabetic Socks (5-pack)", "description": "Non-binding top, seamless toe, moisture control. Recommended by podiatrists. One size fits most.", "category": "clothing", "price": 449.0, "tags": ["socks", "diabetic", "wide-fit", "disability-aid", "seamless", "medical"], "stock": 80},

    # --- BOOKS (10 products) ---
    {"name": "Atomic Habits (Paperback)", "description": "James Clear's bestselling guide to building good habits. Practical, research-backed. 320 pages.", "category": "books", "price": 399.0, "tags": ["self-help", "habits", "productivity", "bestseller", "james-clear"], "stock": 100},
    {"name": "Python Crash Course, 3rd Edition", "description": "Beginner-friendly Python programming with 3 real projects. Covers Python 3.11. Eric Matthes.", "category": "books", "price": 699.0, "tags": ["python", "programming", "beginner", "coding", "technical"], "stock": 50},
    {"name": "Sapiens: A Brief History of Humankind", "description": "Yuval Noah Harari's landmark history of the human species. Paperback. 464 pages.", "category": "books", "price": 449.0, "tags": ["history", "non-fiction", "sapiens", "harari", "bestseller"], "stock": 70},
    {"name": "The Very Hungry Caterpillar (Board Book)", "description": "Eric Carle's classic picture book with tactile die-cut pages. Hardcover board book for ages 1–5.", "category": "books", "price": 299.0, "tags": ["children", "picture-book", "age-1-5", "eric-carle", "classic"], "stock": 90},
    {"name": "Ikigai: The Japanese Secret to a Long Life", "description": "Héctor García and Francesc Miralles. Explores the Japanese philosophy of finding purpose. 208 pages.", "category": "books", "price": 349.0, "tags": ["philosophy", "self-help", "ikigai", "japanese", "purpose"], "stock": 60},
    {"name": "The Design of Everyday Things", "description": "Don Norman's essential UX and design principles book. Revised and expanded edition. 368 pages.", "category": "books", "price": 799.0, "tags": ["design", "ux", "ui", "don-norman", "technical", "product"], "stock": 40},
    {"name": "Diary of a Wimpy Kid Box Set (1–7)", "description": "Jeff Kinney's full 7-book illustrated series. Paperback box set. Ages 8–12.", "category": "books", "price": 1299.0, "tags": ["children", "illustrated", "series", "age-8-12", "wimpy-kid"], "stock": 35},
    {"name": "Deep Work by Cal Newport", "description": "Rules for focused success in a distracted world. Paperback. 304 pages.", "category": "books", "price": 399.0, "tags": ["productivity", "focus", "self-help", "cal-newport", "work"], "stock": 55},
    {"name": "The Lean Startup", "description": "Eric Ries. How continuous innovation creates successful businesses. Paperback. 336 pages.", "category": "books", "price": 449.0, "tags": ["startup", "entrepreneurship", "business", "eric-ries", "lean"], "stock": 65},
    {"name": "Good Night Stories for Rebel Girls", "description": "100 illustrated bedtime stories of extraordinary women. Hardcover. Ages 6+.", "category": "books", "price": 899.0, "tags": ["children", "girls", "inspiring", "illustrated", "age-6-plus", "hardcover"], "stock": 45},

    # --- HOME & KITCHEN (10 products) ---
    {"name": "Bamboo Cutting Board Set (3-piece)", "description": "Antimicrobial bamboo. Small, medium, and large boards with juice grooves. Dishwasher-safe.", "category": "home", "price": 799.0, "tags": ["cutting-board", "bamboo", "eco-friendly", "kitchen", "sustainable"], "stock": 55},
    {"name": "Stainless Steel Water Bottle 750ml", "description": "Double-wall vacuum insulated. Keeps cold 24hr, hot 12hr. BPA-free lid. Powder-coat finish. 6 colours.", "category": "home", "price": 899.0, "tags": ["water-bottle", "stainless-steel", "insulated", "bpa-free", "eco-friendly"], "stock": 80},
    {"name": "Silicone Baking Mat (2-pack)", "description": "Non-stick, non-toxic silicone. Replaces parchment paper. Fits standard oven trays. Dishwasher-safe.", "category": "home", "price": 499.0, "tags": ["baking", "silicone", "non-stick", "eco-friendly", "kitchen"], "stock": 70},
    {"name": "Adjustable Laptop Stand", "description": "6-angle aluminium stand. Folds flat. Ventilated to prevent overheating. For laptops 11–17 inches.", "category": "home", "price": 1199.0, "tags": ["laptop-stand", "ergonomic", "aluminium", "portable", "work-from-home"], "stock": 40},
    {"name": "Compost Bin for Kitchen Counter", "description": "1.5L capacity. Odour-control charcoal filter lid. Stainless steel + plastic liner. Easy to clean.", "category": "home", "price": 649.0, "tags": ["compost", "eco-friendly", "kitchen", "sustainable", "odour-control"], "stock": 45},
    {"name": "Electric Milk Frother", "description": "4-in-1: froth, heat, blend, whisk. Works with all milks including oat and almond. Non-stick jug.", "category": "home", "price": 1399.0, "tags": ["frother", "coffee", "milk", "electric", "kitchen", "latte"], "stock": 35},
    {"name": "Drawer Organiser Set (8-piece)", "description": "Modular interlocking bamboo dividers. Customise drawer layout. Fits most standard drawers.", "category": "home", "price": 599.0, "tags": ["organiser", "drawer", "bamboo", "modular", "home", "declutter"], "stock": 60},
    {"name": "Digital Kitchen Scale (5kg)", "description": "0.1g precision. Tare function. USB rechargeable. Slim profile fits in a drawer. Backlit LCD.", "category": "home", "price": 749.0, "tags": ["scale", "kitchen", "digital", "baking", "cooking", "precision"], "stock": 50},
    {"name": "Reusable Beeswax Food Wraps (6-pack)", "description": "Natural beeswax + organic cotton. Replaces cling film. Washable, compostable. Assorted sizes.", "category": "home", "price": 549.0, "tags": ["beeswax", "eco-friendly", "reusable", "food-wrap", "sustainable", "zero-waste"], "stock": 65},
    {"name": "Air Purifier (HEPA + Activated Carbon)", "description": "3-stage filtration. 200 sqft coverage. Auto mode, sleep mode, filter life indicator. Quiet (25dB).", "category": "home", "price": 3999.0, "tags": ["air-purifier", "hepa", "carbon-filter", "home", "health", "allergen"], "stock": 20},
]


def seed():
    """Write all 50 products to Firestore products collection."""
    products_ref = db.collection("products")
    for i, product in enumerate(PRODUCTS, start=1):
        doc_id = f"prod_{i:03d}"
        # Build GCS image URL — actual images uploaded separately
        product["image_url"] = f"https://storage.googleapis.com/{GCS_BUCKET}/products/{doc_id}.jpg"
        products_ref.document(doc_id).set(product)
        print(f"  ✅ [{i:02d}/50] {product['name']}")

    print(f"\n✅ Seeding complete. {len(PRODUCTS)} products written to Firestore.")


if __name__ == "__main__":
    print("🌱 Seeding ShopGenie product catalog into Firestore...")
    seed()
