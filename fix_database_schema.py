#!/usr/bin/env python3
"""
Database Schema Fix Script
Fixes the missing duration_type column in folder_share_codes table
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

def main():
    """Main function to fix database schema"""
    print("🔧 Database Schema Fix Script")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("   Make sure your .env file contains DATABASE_URL")
        sys.exit(1)
    
    print(f"📊 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # Check current table structure
        print("\n🔍 Checking current folder_share_codes table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'folder_share_codes' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("📋 Current columns:")
        for col_name, data_type, nullable in columns:
            print(f"   - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
        
        # Check if duration_type column exists
        column_names = [col[0] for col in columns]
        has_duration_type = 'duration_type' in column_names
        
        if has_duration_type:
            print("✅ duration_type column already exists!")
        else:
            print("⚠️  duration_type column is missing - adding it now...")
            
            # Add the missing column
            migration_sql = """
            -- Add missing duration_type column
            ALTER TABLE folder_share_codes 
            ADD COLUMN duration_type VARCHAR(10);
            
            -- Copy data from duration column to duration_type
            UPDATE folder_share_codes 
            SET duration_type = duration 
            WHERE duration_type IS NULL;
            
            -- Make duration_type NOT NULL
            ALTER TABLE folder_share_codes 
            ALTER COLUMN duration_type SET NOT NULL;
            
            -- Add index for performance
            CREATE INDEX IF NOT EXISTS idx_folder_share_codes_duration_type 
            ON folder_share_codes(duration_type);
            """
            
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Successfully added duration_type column!")
        
        # Verify the fix
        print("\n🔍 Verifying schema after fix...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'folder_share_codes' 
            ORDER BY ordinal_position;
        """)
        
        updated_columns = cursor.fetchall()
        print("📋 Updated columns:")
        for col_name, data_type, nullable in updated_columns:
            print(f"   - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
        
        # Check if there are any records
        cursor.execute("SELECT COUNT(*) FROM folder_share_codes;")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total records in folder_share_codes: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, share_code, duration, duration_type FROM folder_share_codes LIMIT 3;")
            sample_records = cursor.fetchall()
            print("📋 Sample records:")
            for record in sample_records:
                print(f"   ID: {record[0]}, Code: {record[1]}, Duration: {record[2]}, Duration Type: {record[3]}")
        
        print("\n✅ Database schema fix completed successfully!")
        print("🚀 Your application should now work without the column error.")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("🔒 Database connection closed")

if __name__ == "__main__":
    main()