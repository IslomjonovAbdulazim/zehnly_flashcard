#!/usr/bin/env python3
"""
Database Migration Runner for Vocabulary Learning System
Run this script to create all necessary PostgreSQL tables.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the database migration script"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print("🗄️  Starting database migration...")
    print(f"📡 Connecting to database...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL")
        
        # Read migration file
        migration_file = "migrations/001_initial_vocabulary_system.sql"
        print(f"📜 Reading migration file: {migration_file}")
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("🚀 Executing migration...")
        
        # Execute migration
        cursor.execute(migration_sql)
        
        print("✅ Migration completed successfully!")
        
        # Show created tables
        cursor.execute("""
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('users', 'vocabulary_folders', 'vocabulary_words', 'folder_share_codes', 'folder_followers')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print("\n📊 Created tables:")
        for table_name, column_count in tables:
            print(f"   ✅ {table_name} ({column_count} columns)")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Your vocabulary system is ready to use")
        print("   2. Start your FastAPI server: uvicorn app.main:app --reload")
        print("   3. Test the API endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)