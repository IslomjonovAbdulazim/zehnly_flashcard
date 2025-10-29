# Vocabulary Learning System API Documentation

A scalable FastAPI microservice for vocabulary learning with automatic translation and audio pronunciation generation.

## 🔧 System Limits

**System Limits (All Users):**
- Maximum words per folder: **50** (hard limit)
- Maximum folders per user: **50** (hard limit)

**Plan Limits:**
- **Free users**: Maximum 2 folders (owned + followed combined)
- **Premium users**: Maximum 50 folders (owned + followed combined)

**Error Types:**
- `SYSTEM_LIMIT_EXCEEDED`: Hard limits that cannot be upgraded
- `PLAN_LIMIT_EXCEEDED`: Plan limits that can be upgraded to premium

## 🚀 Authentication

All endpoints require microservice authentication via header:
```
X-User-Id: {user_internal_id}
```

Users are auto-created if they don't exist with default free status.

## ⚠️ Error Response Format

All API errors return a standardized JSON response format:

```json
{
  "error_code": "ERROR_CODE_NAME",
  "message": "Human readable error message"
}
```

**Common Error Codes:**
- `USER_NOT_FOUND` - User does not exist (404)
- `UNAUTHORIZED` - Missing or invalid X-User-Id header (401)
- `VALIDATION_ERROR` - Invalid request data (422)
- `SYSTEM_LIMIT_EXCEEDED` - Hard system limits exceeded (400)
- `PLAN_LIMIT_EXCEEDED` - Plan limits exceeded, upgrade needed (400)
- `INTERNAL_SERVER_ERROR` - Server error (500)

---

## 👤 User Management Endpoints

### Register/Update User
**POST** `/api/v1/users/register`

Register new user or update existing user information.

**Request Body:**
```json
{
  "external_id": "507f1f77bcf86cd799439011",
  "contact": "user@example.com"
}
```

**Response:** `201 Created` (new user) or `200 OK` (updated)
```json
{
  "id": 123,
  "external_id": "507f1f77bcf86cd799439011",
  "contact": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T09:15:00Z"
}
```

### Check User Registration
**GET** `/api/v1/users/check/{external_id}`

Check if a user is registered in the microservice by their external_id.

**Path Parameters:**
- `external_id` (string): MongoDB ObjectId from main service

**Response:** `200 OK` (user exists) or `404 Not Found` (user doesn't exist)
```json
{
  "id": 123,
  "external_id": "507f1f77bcf86cd799439011",
  "contact": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T09:15:00Z"
}
```

**Error Response:** `404 Not Found`
```json
{
  "error_code": "USER_NOT_FOUND",
  "message": "User not found"
}
```

### Get Current User
**GET** `/api/v1/users/me`

Get current user information from X-User-Id header. Auto-creates user if doesn't exist.

**Headers Required:**
```
X-User-Id: 507f1f77bcf86cd799439011
```

**Response:** `200 OK`
```json
{
  "id": 123,
  "external_id": "507f1f77bcf86cd799439011", 
  "contact": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T09:15:00Z"
}
```

---

## 📁 Folder Management Endpoints

### Create Vocabulary Folder
**POST** `/api/v1/folders/`

Create a new vocabulary folder for organizing words by target language.

**Limits:**
- Free users: Maximum 2 total folders
- Premium users: Maximum 50 total folders

**Request Body:**
```json
{
  "title": "Spanish Basics",
  "target_language": "es",
  "is_premium": true
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Spanish Basics",
  "target_language": "es",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "word_count": 0,
  "has_share_code": false
}
```

**Error Responses:**
- `400 SYSTEM_LIMIT_EXCEEDED`: System folder limit (50) exceeded
- `400 PLAN_LIMIT_EXCEEDED`: Plan folder limit exceeded (upgrade to premium)

---

### Get User Folders
**GET** `/api/v1/folders/`

Retrieve all folders accessible to the user (owned + followed).

**Response:** `200 OK`
```json
{
  "owned_folders": [
    {
      "id": 1,
      "user_id": 123,
      "title": "Spanish Basics",
      "target_language": "es",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null,
      "word_count": 15,
      "has_share_code": true,
      "share_code": "AB123",
      "share_expires_at": "2024-01-17T10:30:00Z"
    }
  ],
  "followed_folders": [
    {
      "folder": {
        "id": 2,
        "user_id": 456,
        "title": "French Vocabulary",
        "target_language": "fr",
        "is_active": true,
        "created_at": "2024-01-10T09:15:00Z",
        "updated_at": null,
        "word_count": 8,
        "has_share_code": false
      },
      "joined_at": "2024-01-16T14:20:00Z",
      "joined_via_code": "AB123"
    }
  ]
}
```

---

### Update Folder
**PUT** `/api/v1/folders/{folder_id}`

Update folder details (owner only).

**Request Body:**
```json
{
  "title": "Advanced Spanish",
  "target_language": "es",
  "is_active": true,
  "is_premium": true
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Advanced Spanish",
  "target_language": "es",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T11:45:00Z",
  "word_count": 15,
  "has_share_code": true
}
```

---

### Delete Folder
**DELETE** `/api/v1/folders/{folder_id}`

Delete a folder (owner only).

**Response:** `204 No Content`

---

## 🔗 Share Code Management

### Create Share Code
**POST** `/api/v1/folders/{folder_id}/share`

Generate a deterministic share code for folder sharing.

**Request Body:**
```json
{
  "duration": "24h"
}
```

**Valid durations:** `"10m"`, `"1h"`, `"24h"`, `"72h"`

**Response:** `201 Created`
```json
{
  "share_code": "AB123",
  "expires_at": "2024-01-17T10:30:00Z",
  "duration": "24h"
}
```

---

### Delete Share Code
**DELETE** `/api/v1/folders/{folder_id}/share`

Remove the active share code for a folder (owner only).

**Response:** `204 No Content`

**Error Responses:**
- `404 NOT_FOUND`: No share code exists for this folder

---

### Join Folder via Share Code
**POST** `/api/v1/folders/join`

Join a folder using a share code.

**Limits:**
- Counts towards user's total folder limit
- Free users: 2 total folders, Premium users: 50 total folders

**Request Body:**
```json
{
  "share_code": "AB123",
  "is_premium": true
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "user_id": 456,
  "title": "Shared Spanish Folder",
  "target_language": "es",
  "is_active": true,
  "created_at": "2024-01-10T09:15:00Z",
  "updated_at": null,
  "word_count": 25,
  "has_share_code": false
}
```

**Error Responses:**
- `404 NOT_FOUND`: Invalid or expired share code
- `400 DUPLICATE_OPERATION`: Already following this folder
- `400 DUPLICATE_OPERATION`: Cannot follow your own folder
- `400 SYSTEM_LIMIT_EXCEEDED`: System folder limit (50) exceeded
- `400 PLAN_LIMIT_EXCEEDED`: Plan folder limit exceeded (upgrade to premium)

---

### Unfollow Folder
**DELETE** `/api/v1/folders/{folder_id}/unfollow`

Stop following a folder (removes it from your followed folders list).

**Response:** `204 No Content`

**Error Responses:**
- `404 NOT_FOUND`: You are not following this folder

---

## 📖 Vocabulary Word Management

### Add Word to Folder
**POST** `/api/v1/folders/{folder_id}/words`

Add a new word with automatic translation and audio generation.

**Limits:**
- Maximum 50 words per folder

**Request Body:**
```json
{
  "word": "hello"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "folder_id": 1,
  "original_word": "hello",
  "original_language": "en",
  "translated_word": "hola",
  "target_language": "es",
  "audio_url": "https://storage.googleapis.com/bucket/word_pronunciations/es/abc123.mp3",
  "is_active": true,
  "created_at": "2024-01-16T15:30:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 DUPLICATE_OPERATION`: Word already exists in this folder
- `400 SYSTEM_LIMIT_EXCEEDED`: System word limit (50) exceeded for this folder
- `500 INTERNAL_SERVER_ERROR`: Translation or audio generation failed

---

### Get Folder Words
**GET** `/api/v1/folders/{folder_id}/words`

Retrieve all words in a folder (no pagination - max 50 words per folder).

**Response:** `200 OK`
```json
{
  "words": [
    {
      "id": 1,
      "folder_id": 1,
      "original_word": "hello",
      "original_language": "en",
      "translated_word": "hola",
      "target_language": "es",
      "audio_url": "https://storage.googleapis.com/bucket/word_pronunciations/es/abc123.mp3",
      "is_active": true,
      "created_at": "2024-01-16T15:30:00Z",
      "updated_at": null
    }
  ],
  "total": 15,
  "folder_title": "Spanish Basics",
  "folder_target_language": "es"
}
```

---

### Delete Word
**DELETE** `/api/v1/folders/{folder_id}/words/{word_id}`

Remove a word from a folder.

**Response:** `204 No Content`

**Error Responses:**
- `404 NOT_FOUND`: Word not found in this folder

---

## 📋 Supported Languages

| Code | Language | Default Voice |
|------|----------|---------------|
| `en` | English | Betty |
| `es` | Spanish | Rosa |
| `fr` | French | Celine |
| `de` | German | Vicki |
| `it` | Italian | Carla |
| `pt` | Portuguese | Vitoria |
| `ru` | Russian | Tatyana |
| `ja` | Japanese | Kyoko |
| `ko` | Korean | Seoyeon |
| `zh` | Chinese | Zhiyu |
| `ar` | Arabic | Zeina |
| `hi` | Hindi | Aditi |
| `tr` | Turkish | Filiz |
| `pl` | Polish | Maja |
| `nl` | Dutch | Lotte |

---

## 🔧 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `NOT_FOUND` | 404 | Resource not found or access denied |
| `DUPLICATE_OPERATION` | 400 | Resource already exists or action not allowed |
| `BAD_REQUEST` | 400 | Invalid request data |
| `SYSTEM_LIMIT_EXCEEDED` | 400 | Hard system limit exceeded (cannot upgrade) |
| `PLAN_LIMIT_EXCEEDED` | 400 | Plan limit exceeded (can upgrade to premium) |
| `INTERNAL_SERVER_ERROR` | 500 | Server error or external API failure |

**Error Response Examples:**
```json
{
  "error_code": "PLAN_LIMIT_EXCEEDED",
  "detail": "Plan folder limit (2) exceeded for free account"
}
```

```json
{
  "error_code": "SYSTEM_LIMIT_EXCEEDED", 
  "detail": "System folder limit (50) exceeded"
}
```

---

## 🎯 Share Code System

**Format:** `LLNNN` (2 letters + 3 numbers)
- **Letters:** `ABCDEFGHJKMNPQRSTVWXYZ` (24 letters)
- **Numbers:** `0123456789` (10 digits)
- **Total combinations:** 294,912 unique codes

**Example codes:** `AB123`, `ZY999`, `MN456`

---

## 🚀 Quick Start Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "X-User-Id: 123" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "507f1f77bcf86cd799439011",
    "contact": "user@example.com"
  }'
```

### 2. Create Folder
```bash
curl -X POST "http://localhost:8000/api/v1/folders/" \
  -H "X-User-Id: 123" \
  -H "Content-Type: application/json" \
  -d '{"title": "Spanish Learning", "target_language": "es", "is_premium": true}'
```

### 3. Add Word
```bash
curl -X POST "http://localhost:8000/api/v1/folders/1/words" \
  -H "X-User-Id: 123" \
  -H "Content-Type: application/json" \
  -d '{"word": "hello"}'
```

### 4. Get Words
```bash
curl -X GET "http://localhost:8000/api/v1/folders/1/words" \
  -H "X-User-Id: 123"
```

### 5. Create Share Code
```bash
curl -X POST "http://localhost:8000/api/v1/folders/1/share" \
  -H "X-User-Id: 123" \
  -H "Content-Type: application/json" \
  -d '{"duration": "24h"}'
```

### 6. Join Folder
```bash
curl -X POST "http://localhost:8000/api/v1/folders/join" \
  -H "X-User-Id: 456" \
  -H "Content-Type: application/json" \
  -d '{"share_code": "AB123", "is_premium": false}'
```

### 7. Unfollow Folder
```bash
curl -X DELETE "http://localhost:8000/api/v1/folders/2/unfollow" \
  -H "X-User-Id: 456"
```

---

*Vocabulary Learning System API - Built with FastAPI*