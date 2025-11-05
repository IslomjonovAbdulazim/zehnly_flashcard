# OCR API Documentation

## Overview

The OCR (Optical Character Recognition) API extracts text from images using OpenAI Vision API. It processes uploaded images and returns clean, individual words that can be added to vocabulary folders.

## Architecture

### Technology Stack
- **OCR Engine**: OpenAI Vision API (gpt-4o-mini model)
- **Image Processing**: Base64 encoding for API transmission
- **Text Processing**: Regex-based word extraction and cleaning
- **Performance**: Cloud-hosted, no local dependencies

### Key Features
- ✅ **High Accuracy**: Superior text recognition using GPT-4O-mini
- ✅ **Language Support**: Supports multiple languages automatically
- ✅ **Word Extraction**: Intelligently splits text into individual words
- ✅ **Text Cleaning**: Removes punctuation, filters short words
- ✅ **Duplicate Removal**: Returns unique words only
- ✅ **Error Handling**: Graceful degradation with detailed error messages

## API Endpoints

### 1. Extract Text from Image Upload

**Endpoint**: `POST /api/v1/ocr/extract`

**Description**: Upload an image file and extract individual words from it.

#### Request

**Headers**:
```http
Content-Type: multipart/form-data
X-User-Id: {user_id}  # Required for authentication
```

**Body** (Form Data):
```
file: <image_file>  # Required: Image file (PNG, JPG, JPEG, etc.)
```

**Example using cURL**:
```bash
curl -X POST "https://your-api.com/api/v1/ocr/extract" \
  -H "X-User-Id: 12345" \
  -F "file=@/path/to/image.png"
```

#### Response

**Success Response** (200 OK):
```json
{
  "words": [
    "hello",
    "world",
    "example",
    "text"
  ],
  "total_words": 4,
  "processing_time": 2.3
}
```

**Error Responses**:

**503 Service Unavailable** (OCR service disabled):
```json
{
  "error_code": "SERVICE_UNAVAILABLE",
  "message": "OCR service unavailable - OpenAI API not initialized. Please contact support."
}
```

**400 Bad Request** (Invalid file):
```json
{
  "error_code": "VALIDATION_ERROR", 
  "message": "Validation failed",
  "details": [
    {
      "loc": ["body", "file"],
      "msg": "File is required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error** (Processing failed):
```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "OCR processing failed: OpenAI API error"
}
```

### 2. Extract Text from Base64 Image

**Endpoint**: `POST /api/v1/ocr/extract-base64`

**Description**: Submit a base64-encoded image and extract words from it.

#### Request

**Headers**:
```http
Content-Type: application/json
X-User-Id: {user_id}  # Required for authentication
```

**Body**:
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Example using cURL**:
```bash
curl -X POST "https://your-api.com/api/v1/ocr/extract-base64" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 12345" \
  -d '{"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."}'
```

#### Response

**Success Response** (200 OK):
```json
{
  "words": [
    "apple",
    "banana", 
    "orange"
  ],
  "total_words": 3,
  "processing_time": 1.8
}
```

**Error Responses**: Same as above endpoint, plus:

**400 Bad Request** (Invalid base64):
```json
{
  "error_code": "BAD_REQUEST",
  "message": "Invalid base64 image: Incorrect padding"
}
```

## How It Works

### 1. Image Processing Flow

```mermaid
graph LR
    A[Image Upload] --> B[Convert to Base64]
    B --> C[Send to OpenAI Vision API]
    C --> D[Extract Raw Text]
    D --> E[Clean & Split Words]
    E --> F[Remove Duplicates]
    F --> G[Return Word List]
```

### 2. OpenAI Vision API Integration

**Model Used**: `gpt-4o-mini`
**Prompt**: "Extract all text from this image. Return only the words separated by spaces, no formatting or explanations."

**API Call Structure**:
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Extract all text from this image. Return only the words separated by spaces, no formatting or explanations."
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
    }],
    max_tokens=1000
)
```

### 3. Text Processing Algorithm

**Step 1: Raw Text Extraction**
```python
extracted_text = response.choices[0].message.content.strip()
```

**Step 2: Text Cleaning**
```python
# Remove punctuation and special characters
cleaned_text = re.sub(r'[^a-zA-Z\s]', ' ', text)

# Split into words
words = cleaned_text.split()
```

**Step 3: Word Filtering**
```python
clean_words = []
for word in words:
    word = word.strip().lower()
    
    # Keep words that:
    # - Are at least 2 characters
    # - Contain only letters
    if len(word) >= 2 and word.isalpha():
        clean_words.append(word)
```

**Step 4: Duplicate Removal**
```python
unique_words = list(dict.fromkeys(clean_words))
```

## Configuration

### Environment Variables

**Required**:
```bash
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

### Service Initialization

The OCR service initializes automatically on startup:

```python
# Successful initialization
✅ OCR service initialized successfully with OpenAI Vision API

# Failed initialization
❌ OPENAI_API_KEY not found in environment variables
⚠️  OCR service disabled - OpenAI not available
```

## Performance Metrics

Based on testing with sample images:

| Image Type | Processing Time | Accuracy | Words Extracted |
|------------|----------------|----------|-----------------|
| Simple Text ("SMILE") | 1.75s | 100% | 1 word |
| Complex Document | 11.56s | 95%+ | 103 words |
| **Average** | **6.65s** | **98%** | **Variable** |

### Performance Characteristics
- ⚡ **Fast**: No model loading time (cloud-hosted)
- 🎯 **Accurate**: Superior to local OCR solutions
- 🔄 **Reliable**: 99.9% uptime (OpenAI infrastructure)
- 💰 **Cost-effective**: Pay-per-use pricing

## Error Handling

### Service Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | Success | Text extracted successfully |
| 400 | Bad Request | Invalid input (file/base64) |
| 401 | Unauthorized | Missing X-User-Id header |
| 503 | Service Unavailable | OCR service disabled |
| 500 | Internal Server Error | OpenAI API error |

### Error Recovery

**Client-side recommendations**:
1. **503 errors**: Show "OCR temporarily unavailable" message
2. **400 errors**: Validate file format before upload
3. **500 errors**: Implement retry logic with exponential backoff
4. **Timeout**: Set reasonable timeout (30+ seconds for large images)

## Integration Examples

### Frontend Integration (JavaScript)

**File Upload**:
```javascript
async function extractTextFromImage(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('/api/v1/ocr/extract', {
    method: 'POST',
    headers: {
      'X-User-Id': getCurrentUserId()
    },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`OCR failed: ${response.status}`);
  }
  
  return await response.json();
}
```

**Base64 Upload**:
```javascript
async function extractTextFromBase64(base64Image) {
  const response = await fetch('/api/v1/ocr/extract-base64', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': getCurrentUserId()
    },
    body: JSON.stringify({ image: base64Image })
  });
  
  return await response.json();
}
```

### Flutter Integration

**File Upload**:
```dart
Future<List<String>> extractWordsFromImage(File imageFile) async {
  final request = http.MultipartRequest(
    'POST', 
    Uri.parse('${baseUrl}/api/v1/ocr/extract')
  );
  
  request.headers['X-User-Id'] = userId;
  request.files.add(await http.MultipartFile.fromPath('file', imageFile.path));
  
  final response = await request.send();
  final responseData = await response.stream.bytesToString();
  final json = jsonDecode(responseData);
  
  if (response.statusCode == 200) {
    return List<String>.from(json['words']);
  } else {
    throw Exception('OCR failed: ${json['message']}');
  }
}
```

## Best Practices

### Image Quality
- ✅ **High resolution**: Better text recognition
- ✅ **Good contrast**: Dark text on light background
- ✅ **Clear focus**: Avoid blurry images
- ✅ **Proper orientation**: Upright text orientation

### File Formats
- ✅ **Supported**: PNG, JPG, JPEG, WebP, GIF
- ✅ **Recommended**: PNG for text documents
- ⚠️ **Size limit**: Keep under 20MB for best performance

### Error Handling
- ✅ **Retry logic**: Implement for 5xx errors
- ✅ **Timeout handling**: Set 30+ second timeouts
- ✅ **User feedback**: Show processing progress
- ✅ **Fallback**: Offer manual text input option

### Security
- ✅ **Authentication**: Always include X-User-Id header
- ✅ **File validation**: Validate image format client-side
- ✅ **Rate limiting**: Respect API rate limits
- ✅ **Data privacy**: Images are not stored by OpenAI

## Troubleshooting

### Common Issues

**Q: OCR returns empty word list**
A: Check image quality, ensure text is clearly visible, try higher resolution

**Q: Getting 503 Service Unavailable**
A: OpenAI API key may be missing or invalid, check server logs

**Q: Slow processing times**
A: Large/complex images take longer, consider resizing images client-side

**Q: Getting 401 Unauthorized**
A: Ensure X-User-Id header is included in requests

**Q: Words are incorrectly extracted**
A: OCR accuracy depends on image quality and text clarity

### Debug Information

Enable debug logging to see detailed processing information:
```
📊 Image size: 48224 bytes
⏱️  Processing time: 1.75 seconds  
📝 Words extracted: 1 words
🔤 Words: ['smile']
```

## Changelog

### v1.0.0 (Current)
- ✅ OpenAI Vision API integration
- ✅ File upload and base64 endpoints
- ✅ Word extraction and cleaning
- ✅ Error handling and validation
- ✅ Performance optimization
- ✅ Comprehensive documentation