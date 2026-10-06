import os

class Settings:
    PROJECT_NAME: str = "HostelIQ: Smart Hostel Resource & Complaint Analytics System"
    VERSION: str = "1.0.0"
    
    # SQL Database Configuration (Supports SQLite local file & MySQL connection)
    SQL_DB_FILE: str = os.getenv("SQL_DB_FILE", "hosteliq.db")
    SQL_DATABASE_URL: str = os.getenv("SQL_DATABASE_URL", f"sqlite:///{SQL_DB_FILE}")
    
    # MongoDB Configuration (Supports local MongoDB or fallback mock database)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "hosteliq_nosql")

settings = Settings()
