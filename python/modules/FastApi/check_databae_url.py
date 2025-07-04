from sqlalchemy import create_engine

# Replace this with your actual credentials
DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/films_db"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("✅ Connection successful!")
    connection.close()
except Exception as e:
    print("❌ Connection failed:", e)