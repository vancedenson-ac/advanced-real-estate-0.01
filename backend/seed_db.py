"""Script to seed database with mock data."""
from app.database import SessionLocal, init_db
from app.fixtures.seed_data import seed_all

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("\nSeeding database...")
    db = SessionLocal()
    try:
        seed_all(db, num_listings=5, images_per_listing=3, conversations_per_listing=2)
    finally:
        db.close()
    
    print("\nDone!")

