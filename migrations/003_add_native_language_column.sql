-- Migration: 003_add_native_language_column.sql
-- Description: Add native_language column to vocabulary_folders table

-- Add the native_language column to vocabulary_folders table
ALTER TABLE vocabulary_folders 
ADD COLUMN IF NOT EXISTS native_language VARCHAR(50);

-- Update existing records to set default native_language to 'uz'
UPDATE vocabulary_folders 
SET native_language = 'uz' 
WHERE native_language IS NULL;

-- Make native_language NOT NULL after populating existing records
ALTER TABLE vocabulary_folders 
ALTER COLUMN native_language SET NOT NULL;

-- Set default value for future inserts
ALTER TABLE vocabulary_folders 
ALTER COLUMN native_language SET DEFAULT 'uz';

-- Create index for the new column to improve query performance
CREATE INDEX IF NOT EXISTS idx_vocabulary_folders_native_language 
ON vocabulary_folders(native_language);

-- Create composite index for common query patterns (target + native language)
CREATE INDEX IF NOT EXISTS idx_vocabulary_folders_languages 
ON vocabulary_folders(target_language, native_language);

COMMIT;