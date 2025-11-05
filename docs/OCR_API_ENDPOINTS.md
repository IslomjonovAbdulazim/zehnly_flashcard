# OCR API Endpoints

## 1. Extract Text from Image File

**POST** `/api/v1/ocr/extract`

### Request
**Headers:**
```
Content-Type: multipart/form-data
X-User-Id: {user_id}
```

**Body (Form Data):**
```
file: <image_file>
```

### Response
**Success (200):**
```json
{
  "words": [
    "hello",
    "world",
    "example"
  ],
  "total_words": 3,
  "processing_time": 2.1
}
```

**Error (503):**
```json
{
  "error_code": "SERVICE_UNAVAILABLE",
  "message": "OCR service unavailable - OpenAI API not initialized. Please contact support."
}
```

**Error (400):**
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

**Error (500):**
```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "OCR processing failed: OpenAI API error"
}
```

---

## 2. Extract Text from Base64 Image

**POST** `/api/v1/ocr/extract-base64`

### Request
**Headers:**
```
Content-Type: application/json
X-User-Id: {user_id}
```

**Body:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### Response
**Success (200):**
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

**Error (400) - Invalid Base64:**
```json
{
  "error_code": "BAD_REQUEST",
  "message": "Invalid base64 image: Incorrect padding"
}
```

**Other errors:** Same as above endpoint

---

## Integration Examples

### JavaScript
```javascript
// File upload
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('/api/v1/ocr/extract', {
  method: 'POST',
  headers: { 'X-User-Id': userId },
  body: formData
});

const result = await response.json();
```

### Flutter
```dart
// File upload
final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/v1/ocr/extract'));
request.headers['X-User-Id'] = userId;
request.files.add(await http.MultipartFile.fromPath('file', imageFile.path));

final response = await request.send();
final json = jsonDecode(await response.stream.bytesToString());
```