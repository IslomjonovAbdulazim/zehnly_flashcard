-- Vocabulary Learning System Database Schema
-- Migration: 001_initial_vocabulary_system.sql
-- Description: Creates all tables for the vocabulary learning microservice

-- Drop tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS vocabulary_words CASCADE;
DROP TABLE IF EXISTS folder_share_codes CASCADE;
DROP TABLE IF EXISTS folder_followers CASCADE;
DROP TABLE IF EXISTS vocabulary_folders CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table (microservice users)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,  -- MongoDB ObjectId from main service
    contact VARCHAR(255),                      -- Email or contact info
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vocabulary folders table
CREATE TABLE vocabulary_folders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    target_language VARCHAR(10) NOT NULL,      -- Language code (es, fr, en, etc.)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vocabulary words table
CREATE TABLE vocabulary_words (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER NOT NULL REFERENCES vocabulary_folders(id) ON DELETE CASCADE,
    original_word VARCHAR(255) NOT NULL,
    original_language VARCHAR(10),             -- Detected source language
    translated_word VARCHAR(255) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    audio_url TEXT,                            -- Public URL to audio file
    audio_path TEXT,                           -- Storage path for audio file
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Folder share codes table (for sharing folders)
CREATE TABLE folder_share_codes (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER UNIQUE NOT NULL REFERENCES vocabulary_folders(id) ON DELETE CASCADE,
    share_code VARCHAR(10) UNIQUE NOT NULL,   -- Format: LLNNN (e.g., AB123)
    duration VARCHAR(10) NOT NULL,            -- Duration string (10m, 1h, 24h, 72h)
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Folder followers table (users following shared folders)
CREATE TABLE folder_followers (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER NOT NULL REFERENCES vocabulary_folders(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_via_code VARCHAR(10),              -- Share code used to join
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure user can only follow a folder once
    UNIQUE(folder_id, user_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_vocabulary_folders_user_id ON vocabulary_folders(user_id);
CREATE INDEX idx_vocabulary_folders_active ON vocabulary_folders(is_active);
CREATE INDEX idx_vocabulary_folders_user_active ON vocabulary_folders(user_id, is_active);

CREATE INDEX idx_vocabulary_words_folder_id ON vocabulary_words(folder_id);
CREATE INDEX idx_vocabulary_words_active ON vocabulary_words(is_active);
CREATE INDEX idx_vocabulary_words_folder_active ON vocabulary_words(folder_id, is_active);
CREATE INDEX idx_vocabulary_words_original ON vocabulary_words(original_word);
CREATE INDEX idx_vocabulary_words_translated ON vocabulary_words(translated_word);

CREATE INDEX idx_folder_share_codes_code ON folder_share_codes(share_code);
CREATE INDEX idx_folder_share_codes_folder ON folder_share_codes(folder_id);
CREATE INDEX idx_folder_share_codes_active ON folder_share_codes(is_active);
CREATE INDEX idx_folder_share_codes_expires ON folder_share_codes(expires_at);

CREATE INDEX idx_folder_followers_user ON folder_followers(user_id);
CREATE INDEX idx_folder_followers_folder ON folder_followers(folder_id);
CREATE INDEX idx_folder_followers_active ON folder_followers(is_active);
CREATE INDEX idx_folder_followers_user_active ON folder_followers(user_id, is_active);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vocabulary_folders_updated_at 
    BEFORE UPDATE ON vocabulary_folders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vocabulary_words_updated_at 
    BEFORE UPDATE ON vocabulary_words 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_folder_share_codes_updated_at 
    BEFORE UPDATE ON folder_share_codes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing (optional)
-- Uncomment the following lines if you want sample data

/*
INSERT INTO users (external_id, contact) VALUES 
('507f1f77bcf86cd799439011', 'john@example.com'),
('507f1f77bcf86cd799439012', 'jane@example.com');

INSERT INTO vocabulary_folders (user_id, title, target_language) VALUES 
(1, 'Spanish Basics', 'es'),
(1, 'French Learning', 'fr'),
(2, 'German Words', 'de');

INSERT INTO vocabulary_words (folder_id, original_word, original_language, translated_word, target_language) VALUES 
(1, 'hello', 'en', 'hola', 'es'),
(1, 'book', 'en', 'libro', 'es'),
(1, 'water', 'en', 'agua', 'es'),
(2, 'hello', 'en', 'bonjour', 'fr'),
(2, 'book', 'en', 'livre', 'fr'),
(3, 'hello', 'en', 'hallo', 'de');
*/

-- Show created tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('users', 'vocabulary_folders', 'vocabulary_words', 'folder_share_codes', 'folder_followers')
ORDER BY table_name;

COMMIT;