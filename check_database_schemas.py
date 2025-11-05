#!/usr/bin/env python3
"""
Database Schema Checker Script
Analyzes all tables and compares with SQLAlchemy models
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

def check_table_schema(cursor, table_name):
    """Check schema for a specific table"""
    print(f"\n📋 Table: {table_name}")
    print("-" * 40)
    
    # Get column information
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable, 
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position;
    """, (table_name,))
    
    columns = cursor.fetchall()
    
    if not columns:
        print(f"❌ Table '{table_name}' does not exist!")
        return False
    
    for col_name, data_type, max_length, nullable, default in columns:
        length_info = f"({max_length})" if max_length else ""
        null_info = "NULL" if nullable == 'YES' else "NOT NULL"
        default_info = f" DEFAULT {default}" if default else ""
        print(f"   {col_name}: {data_type}{length_info} {null_info}{default_info}")
    
    # Get indexes
    cursor.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = %s 
        ORDER BY indexname;
    """, (table_name,))
    
    indexes = cursor.fetchall()
    if indexes:
        print("\n🔍 Indexes:")
        for idx_name, idx_def in indexes:
            if not idx_name.endswith('_pkey'):  # Skip primary key indexes
                print(f"   {idx_name}")
    
    # Get foreign keys
    cursor.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name = %s;
    """, (table_name,))
    
    foreign_keys = cursor.fetchall()
    if foreign_keys:
        print("\n🔗 Foreign Keys:")
        for col, ref_table, ref_col in foreign_keys:
            print(f"   {col} -> {ref_table}.{ref_col}")
    
    return True

def main():
    """Main function to check all database schemas"""
    print("🔍 Database Schema Checker")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📊 Found {len(tables)} tables: {', '.join(tables)}")
        
        # Expected tables from our models
        expected_tables = [
            'users',
            'vocabulary_folders', 
            'vocabulary_words',
            'folder_share_codes',
            'folder_followers'
        ]
        
        # Check each expected table
        for table in expected_tables:
            if table in tables:
                check_table_schema(cursor, table)
            else:
                print(f"\n❌ Missing table: {table}")
        
        # Check for unexpected tables
        unexpected_tables = set(tables) - set(expected_tables)
        if unexpected_tables:
            print(f"\n⚠️  Unexpected tables found: {', '.join(unexpected_tables)}")
            for table in unexpected_tables:
                check_table_schema(cursor, table)
        
        # Specific check for the problematic column
        print("\n" + "=" * 50)
        print("🎯 SPECIFIC CHECK: folder_share_codes.duration_type")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'folder_share_codes' 
                AND column_name IN ('duration', 'duration_type');
        """)
        
        duration_columns = [row[0] for row in cursor.fetchall()]
        
        print("📋 Duration-related columns found:")
        for col in duration_columns:
            print(f"   ✅ {col}")
        
        if 'duration_type' not in duration_columns:
            print("❌ PROBLEM: duration_type column is missing!")
            print("💡 SOLUTION: Run the fix_database_schema.py script")
        else:
            print("✅ duration_type column exists - schema should be OK")
        
        print("\n🏁 Schema check completed!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()