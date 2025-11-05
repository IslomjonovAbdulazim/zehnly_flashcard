-- Migration: 002_add_duration_type_column.sql
-- Description: Add missing duration_type column to folder_share_codes table

-- Add the missing duration_type column to folder_share_codes table
ALTER TABLE folder_share_codes 
ADD COLUMN IF NOT EXISTS duration_type VARCHAR(10);

-- Update existing records to use the duration value for duration_type
UPDATE folder_share_codes 
SET duration_type = duration 
WHERE duration_type IS NULL;

-- Make duration_type NOT NULL after populating existing records
ALTER TABLE folder_share_codes 
ALTER COLUMN duration_type SET NOT NULL;

-- Create index for the new column
CREATE INDEX IF NOT EXISTS idx_folder_share_codes_duration_type 
ON folder_share_codes(duration_type);

COMMIT;