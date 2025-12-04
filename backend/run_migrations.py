"""Run Alembic migrations."""
import subprocess
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def run_migrations():
    """Run Alembic migrations."""
    try:
        # Check if alembic directory exists
        if not os.path.exists("alembic"):
            print("⚠️  Alembic not initialized. Creating initial migration...")
            # Initialize Alembic
            subprocess.run(["alembic", "init", "alembic"], check=True)
            print("✅ Alembic initialized")
        
        # Create initial migration if needed
        print("🔄 Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Migrations completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("⚠️  Alembic not installed. Using init_db.py instead...")
        from app.database import init_db
        init_db()
        print("✅ Database initialized using init_db.py")

if __name__ == "__main__":
    run_migrations()

