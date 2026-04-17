import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

EDGE_PRODUCTS = [
    {"id": "edge_001", "name": "Bamboo Toothbrush Set (4-pack)", "description": "100% biodegradable bamboo handle, BPA-free bristles. Adult medium. Carbon-neutral shipping.", "category": "home", "price": 299.0, "tags": ["eco-friendly", "bamboo", "sustainable", "zero-waste", "dental"], "image_url": "https://placehold.co/400x300/4c9a2a/ffffff?text=Bamboo+Toothbrushes"},
    {"id": "edge_002", "name": "Tactile Alphabet Flashcards (Braille)", "description": "Dual print + Braille alphabet cards for children. 26 cards with textured letters. Ages 4+.", "category": "toys", "price": 449.0, "tags": ["braille", "disability-aid", "accessible", "educational", "alphabet", "age-4-plus"], "image_url": "https://placehold.co/400x300/e9c46a/264653?text=Braille+Cards"},
]

def seed_edge_cases():
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    if not project_id:
        print("❌ FIREBASE_PROJECT_ID environment variable is not set.")
        sys.exit(1)
        
    cred = None
    if os.path.exists("service-account.json"):
        cred = credentials.Certificate("service-account.json")
        
    if not firebase_admin._apps:
        firebase_admin.initialize_app(
            credential=cred,
            options={"projectId": project_id}
        )

    db = firestore.client()
    products_ref = db.collection("products")
    
    print("🌱 Seeding edge-case products...")
    
    for product in EDGE_PRODUCTS:
        doc_id = product.pop("id")
        products_ref.document(doc_id).set(product)
        print(f"  - Added {product['name']}")
        
    print("✨ Edge case seeding complete!")

if __name__ == "__main__":
    seed_edge_cases()
