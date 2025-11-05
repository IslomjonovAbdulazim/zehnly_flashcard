#!/usr/bin/env python3
"""
Database Schema Manager
Comprehensive tool to check and fix database schema issues
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv
import argparse

class DatabaseSchemaManager:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        self.conn = None
        self.cursor = None
        
        if not self.database_url:
            print("❌ DATABASE_URL not found in environment variables")
            sys.exit(1)
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("✅ Connected to database successfully")
            return True
        except psycopg2.Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed")
    
    def check_table_exists(self, table_name):
        """Check if table exists"""
        self.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table_name,))
        return self.cursor.fetchone()[0]
    
    def check_column_exists(self, table_name, column_name):
        """Check if column exists in table"""
        self.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s 
                AND column_name = %s
            );
        """, (table_name, column_name))
        return self.cursor.fetchone()[0]
    
    def get_table_columns(self, table_name):
        """Get all columns for a table"""
        self.cursor.execute("""
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
        return self.cursor.fetchall()
    
    def fix_folder_share_codes_schema(self):
        """Fix the folder_share_codes table schema"""
        print("\n🔧 Fixing folder_share_codes schema...")
        
        if not self.check_table_exists('folder_share_codes'):
            print("❌ folder_share_codes table does not exist!")
            return False
        
        fixes_needed = []
        
        # Check if duration_type column exists
        if not self.check_column_exists('folder_share_codes', 'duration_type'):
            fixes_needed.append("duration_type")
        
        # Check if created_by column exists
        if not self.check_column_exists('folder_share_codes', 'created_by'):
            fixes_needed.append("created_by")
        
        if not fixes_needed:
            print("✅ All required columns already exist")
            return True
        
        print(f"⚠️  Adding missing columns: {', '.join(fixes_needed)}")
        
        try:
            migration_parts = []
            
            # Add duration_type column if missing
            if "duration_type" in fixes_needed:
                migration_parts.append("""
                -- Add missing duration_type column
                ALTER TABLE folder_share_codes 
                ADD COLUMN IF NOT EXISTS duration_type VARCHAR(10);
                
                -- Copy data from duration column to duration_type (if duration column exists)
                UPDATE folder_share_codes 
                SET duration_type = COALESCE(duration, '24h')
                WHERE duration_type IS NULL;
                
                -- Make duration_type NOT NULL
                ALTER TABLE folder_share_codes 
                ALTER COLUMN duration_type SET NOT NULL;
                
                -- Add index for performance
                CREATE INDEX IF NOT EXISTS idx_folder_share_codes_duration_type 
                ON folder_share_codes(duration_type);
                """)
            
            # Add created_by column if missing
            if "created_by" in fixes_needed:
                migration_parts.append("""
                -- Add missing created_by column
                ALTER TABLE folder_share_codes 
                ADD COLUMN IF NOT EXISTS created_by INTEGER;
                
                -- Set a default value for existing records (user_id 1 or first user)
                UPDATE folder_share_codes 
                SET created_by = (
                    SELECT u.id 
                    FROM users u 
                    INNER JOIN vocabulary_folders vf ON vf.user_id = u.id 
                    WHERE vf.id = folder_share_codes.folder_id 
                    LIMIT 1
                )
                WHERE created_by IS NULL;
                
                -- Make created_by NOT NULL
                ALTER TABLE folder_share_codes 
                ALTER COLUMN created_by SET NOT NULL;
                
                -- Add foreign key constraint
                ALTER TABLE folder_share_codes 
                ADD CONSTRAINT fk_folder_share_codes_created_by 
                FOREIGN KEY (created_by) REFERENCES users(id);
                
                -- Add index for performance
                CREATE INDEX IF NOT EXISTS idx_folder_share_codes_created_by 
                ON folder_share_codes(created_by);
                """)
            
            # Execute all migrations
            migration_sql = "\n".join(migration_parts)
            self.cursor.execute(migration_sql)
            self.conn.commit()
            print(f"✅ Successfully added missing columns: {', '.join(fixes_needed)}")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Failed to add missing columns: {e}")
            self.conn.rollback()
            return False
    
    def check_missing_columns(self):
        """Check for any missing columns in our expected schema"""
        print("\n🔍 Checking for missing columns...")
        
        # Expected schema based on SQLAlchemy models
        expected_schema = {
            'users': ['id', 'external_id', 'contact', 'is_active', 'created_at', 'updated_at'],
            'vocabulary_folders': ['id', 'user_id', 'title', 'target_language', 'is_active', 'created_at', 'updated_at'],
            'vocabulary_words': ['id', 'folder_id', 'original_word', 'original_language', 'translated_word', 'target_language', 'audio_url', 'audio_path', 'is_active', 'created_at', 'updated_at'],
            'folder_share_codes': ['id', 'folder_id', 'share_code', 'expires_at', 'duration_type', 'is_active', 'created_at', 'created_by'],
            'folder_followers': ['id', 'folder_id', 'user_id', 'joined_via_code', 'is_active', 'joined_at']
        }
        
        issues_found = []
        
        for table_name, expected_columns in expected_schema.items():
            if not self.check_table_exists(table_name):
                issues_found.append(f"❌ Missing table: {table_name}")
                continue
            
            print(f"\n📋 Checking {table_name}...")
            actual_columns = [col[0] for col in self.get_table_columns(table_name)]
            
            missing_columns = set(expected_columns) - set(actual_columns)
            extra_columns = set(actual_columns) - set(expected_columns)
            
            if missing_columns:
                for col in missing_columns:
                    issues_found.append(f"❌ Missing column: {table_name}.{col}")
                    print(f"   ❌ Missing: {col}")
            
            if extra_columns:
                for col in extra_columns:
                    print(f"   ⚠️  Extra: {col}")
            
            if not missing_columns and not extra_columns:
                print(f"   ✅ All expected columns present")
        
        return issues_found
    
    def show_schema_summary(self):
        """Show a summary of all database schemas"""
        print("\n📊 Database Schema Summary")
        print("=" * 50)
        
        # Get all tables
        self.cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = self.cursor.fetchall()
        
        for table_name, column_count in tables:
            print(f"\n📋 {table_name} ({column_count} columns)")
            columns = self.get_table_columns(table_name)
            for col_name, data_type, max_length, nullable, default in columns:
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == 'YES' else "NOT NULL"
                print(f"   {col_name}: {data_type}{length_info} {null_info}")
    
    def run_check(self):
        """Run comprehensive schema check"""
        print("🔍 Running comprehensive schema check...")
        
        if not self.connect():
            return False
        
        try:
            # Check for missing columns
            issues = self.check_missing_columns()
            
            # Show summary
            self.show_schema_summary()
            
            if issues:
                print("\n❌ Issues found:")
                for issue in issues:
                    print(f"   {issue}")
                print("\n💡 Run with --fix to attempt automatic fixes")
                return False
            else:
                print("\n✅ No schema issues found!")
                return True
                
        finally:
            self.disconnect()
    
    def run_fix(self):
        """Run schema fixes"""
        print("🔧 Running schema fixes...")
        
        if not self.connect():
            return False
        
        try:
            # Fix folder_share_codes schema
            success = self.fix_folder_share_codes_schema()
            
            if success:
                print("\n✅ Schema fixes completed successfully!")
                print("🚀 Your application should now work without column errors")
            else:
                print("\n❌ Some fixes failed - check the errors above")
            
            return success
            
        finally:
            self.disconnect()

def main():
    parser = argparse.ArgumentParser(description='Database Schema Manager')
    parser.add_argument('--fix', action='store_true', help='Fix schema issues automatically')
    parser.add_argument('--check', action='store_true', help='Check schema for issues (default)')
    
    args = parser.parse_args()
    
    manager = DatabaseSchemaManager()
    
    if args.fix:
        success = manager.run_fix()
    else:
        success = manager.run_check()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()