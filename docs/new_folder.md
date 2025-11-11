# Folder Management API - Updated Endpoints

## Overview
The folder creation and management endpoints have been updated to include `native_language` support. Users can now specify their native language when creating folders, with "uz" (Uzbek) as the default.

## Updated Request/Response Schema

### Create Folder Request Body
```json
{
  "title": "string",
  "target_language": "string",
  "native_language": "string",  // NEW: defaults to "uz"
  "is_premium": boolean
}
```

### Update Folder Request Body  
```json
{
  "title": "string",               // optional
  "target_language": "string",     // optional
  "native_language": "string",     // NEW: optional
  "is_active": boolean,            // optional
  "is_premium": boolean            // optional
}
```

### Folder Response
```json
{
  "id": number,
  "user_id": number,
  "title": "string",
  "target_language": "string",
  "native_language": "string",     // NEW: user's native language
  "is_active": boolean,
  "created_at": "datetime",
  "updated_at": "datetime",
  "word_count": number,            // optional
  "has_share_code": boolean        // optional
}
```

## Endpoints Changed

### POST `/api/v1/folders/`
**Create a new vocabulary folder**

- **Request Body**: Updated to include `native_language` field (defaults to "uz")
- **Response**: Now includes `native_language` in folder response

**Example Request:**
```json
{
  "title": "Spanish Learning",
  "target_language": "Spanish", 
  "native_language": "uz",
  "is_premium": false
}
```

### PUT `/api/v1/folders/{folder_id}`
**Update an existing folder**

- **Request Body**: Now accepts optional `native_language` field
- **Response**: Updated folder data including `native_language`

### GET `/api/v1/folders/{folder_id}`
**Get specific folder**

- **Response**: Now includes `native_language` field

### GET `/api/v1/folders/`
**Get all user folders**

- **Response**: All folders in the response now include `native_language` field

## Database Changes

### Migration: 003_add_native_language_column.sql
- Adds `native_language` column to `vocabulary_folders` table
- Sets default value "uz" for existing records
- Creates indexes for improved query performance
- Sets column as NOT NULL with default value

### Performance Improvements
- New index on `native_language` column
- Composite index on `(target_language, native_language)` for common query patterns

## Backward Compatibility
- **Existing API calls**: Will work without modification (native_language defaults to "uz")
- **Existing data**: All existing folders will have native_language set to "uz" automatically
- **Client updates**: Optional - clients can choose to specify native_language or rely on default

## Usage Examples

### Create folder with default native language:
```json
POST /api/v1/folders/
{
  "title": "French Vocabulary",
  "target_language": "French",
  "is_premium": false
}
// native_language will default to "uz"
```

### Create folder with specific native language:
```json
POST /api/v1/folders/
{
  "title": "German Learning", 
  "target_language": "German",
  "native_language": "en",
  "is_premium": true
}
```

### Update folder's native language:
```json
PUT /api/v1/folders/123
{
  "native_language": "ru"
}
```