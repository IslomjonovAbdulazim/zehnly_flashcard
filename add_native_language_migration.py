#!/usr/bin/env python3
"""
Add native_language column to vocabulary_folders table
Sets 'uz' as default for all existing folders
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_native_language_migration():
    """Add native_language column and set uz for existing folders"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("   Make sure your .env file contains DATABASE_URL")
        return False
    
    print("🗄️  Starting native_language migration...")
    print(f"📡 Connecting to database...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL")
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vocabulary_folders' 
            AND column_name = 'native_language';
        """)
        
        if cursor.fetchone():
            print("⚠️  native_language column already exists!")
            cursor.close()
            conn.close()
            return True
        
        # Count existing folders
        cursor.execute("SELECT COUNT(*) FROM vocabulary_folders;")
        folder_count = cursor.fetchone()[0]
        print(f"📊 Found {folder_count} existing folders")
        
        print("🚀 Adding native_language column...")
        
        # Add the native_language column
        cursor.execute("""
            ALTER TABLE vocabulary_folders 
            ADD COLUMN native_language VARCHAR(50);
        """)
        print("✅ Added native_language column")
        
        # Update existing records to 'uz'
        print("🔄 Setting native_language = 'uz' for existing folders...")
        cursor.execute("""
            UPDATE vocabulary_folders 
            SET native_language = 'uz' 
            WHERE native_language IS NULL;
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} folders with native_language = 'uz'")
        
        # Make column NOT NULL
        print("🔒 Making native_language column NOT NULL...")
        cursor.execute("""
            ALTER TABLE vocabulary_folders 
            ALTER COLUMN native_language SET NOT NULL;
        """)
        
        # Set default value
        print("⚙️  Setting default value to 'uz'...")
        cursor.execute("""
            ALTER TABLE vocabulary_folders 
            ALTER COLUMN native_language SET DEFAULT 'uz';
        """)
        
        # Create performance indexes
        print("🔍 Creating performance indexes...")
        
        # Index on native_language
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vocabulary_folders_native_language 
            ON vocabulary_folders(native_language);
        """)
        
        # Composite index for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vocabulary_folders_languages 
            ON vocabulary_folders(target_language, native_language);
        """)
        
        print("✅ Created performance indexes")
        
        # Verify the changes
        cursor.execute("""
            SELECT 
                COUNT(*) as total_folders,
                COUNT(CASE WHEN native_language = 'uz' THEN 1 END) as uz_folders
            FROM vocabulary_folders;
        """)
        
        total, uz_folders = cursor.fetchone()
        
        print(f"\n📊 Migration Results:")
        print(f"   📁 Total folders: {total}")
        print(f"   🇺🇿 Folders with uz language: {uz_folders}")
        
        # Show column info
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'vocabulary_folders' 
            AND column_name IN ('target_language', 'native_language')
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Updated Column Schema:")
        for col_name, data_type, nullable, default in columns:
            print(f"   {col_name}: {data_type}, nullable={nullable}, default={default}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Native language migration completed successfully!")
        print("\n📋 Summary:")
        print(f"   ✅ Added native_language column to vocabulary_folders")
        print(f"   ✅ Set 'uz' for {updated_count} existing folders")
        print(f"   ✅ Made column NOT NULL with default 'uz'")
        print(f"   ✅ Created performance indexes")
        print(f"\n🚀 Your API now supports native_language field!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        print(f"📝 Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = run_native_language_migration()
    exit(0 if success else 1)