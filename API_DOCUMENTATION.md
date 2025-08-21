# easeCHAOS API Documentation

This documentation provides information about the API structure and usage for frontend developers who want to integrate with the easeCHAOS backend.

## Table of Contents
1. [API Overview](#api-overview)
2. [Base URL](#base-url)
3. [API Endpoints](#api-endpoints)
   - [Health Check](#health-check)
   - [Get Timetable](#get-timetable)
4. [Data Structure](#data-structure)
   - [Request Format](#request-format)
   - [Response Format](#response-format)
5. [Database Configuration](#database-configuration)
6. [Excel File Structure](#excel-file-structure)
7. [Error Handling](#error-handling)

## API Overview

The easeCHAOS API is a FastAPI-based backend service that provides timetable data for UMaT students. It processes Excel files containing lecture and exam schedules and returns structured JSON data that can be easily consumed by frontend applications.

## Base URL

All API endpoints are prefixed with `/api/v1`. For example, if your server is running on `localhost:3000`, the base URL would be:
```
http://localhost:3000/api/v1
```

## API Endpoints

### Health Check

**Endpoint:** `GET /api/v1/healthcheck`

**Description:** Check if the API server is running and healthy.

**Response:**
```json
{
  "status": "healthy"
}
```

### Get Timetable

**Endpoint:** `POST /api/v1/get_time_table`

**Description:** Retrieve timetable data (lectures or exams) for a specific class from an Excel file.

**Request Body:**
```json
{
  "filename": "Draft_1.xlsx",
  "class_pattern": "EL 3",
  "is_exam": false
}
```

**Parameters:**
- `filename` (string, required): Name of the Excel file containing the timetable data.
- `class_pattern` (string, required): Class identifier to filter the timetable (e.g., "EL 3").
- `is_exam` (boolean, optional): Whether to retrieve exam timetable instead of lecture timetable. Defaults to `false`.

**Response Format:**
```json
{
  "data": [
    {
      "day": "Monday",
      "data": [
        {
          "start": "08:00",
          "end": "09:00",
          "value": "Course Name",
          "class": "Class Name",
          "location": "Room 101",
          "invigilator": "Dr. Smith"  // Only for exams
        }
      ]
    }
  ],
  "version": "md5_hash_of_file"
}
```

**Response Fields:**
- `data`: Array of daily schedules
  - `day`: Day of the week (e.g., "Monday")
  - `data`: Array of time slots for that day
    - `start`: Start time in 24-hour format (HH:MM)
    - `end`: End time in 24-hour format (HH:MM)
    - `value`: Course name or activity
    - `class`: Class identifier
    - `location`: Lecture hall or venue (exams only)
    - `invigilator`: Exam supervisor (exams only)
- `version`: MD5 hash of the source Excel file for cache validation

## Data Structure

### Request Format

The API expects a JSON payload with the following structure:

```json
{
  "filename": "string",
  "class_pattern": "string",
  "is_exam": "boolean (optional)"
}
```

### Response Format

The API returns a JSON response with the following structure:

```json
{
  "data": [
    {
      "day": "string",
      "data": [
        {
          "start": "HH:MM",
          "end": "HH:MM",
          "value": "string",
          "class": "string",
          "location": "string (exams only)",
          "invigilator": "string (exams only)"
        }
      ]
    }
  ],
  "version": "string"
}
```

## Database Configuration

The API uses PostgreSQL for caching timetable data. The database configuration is set through environment variables:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=easechaos
DB_USER=postgres
DB_PASSWORD=password
```

The cache table structure:
```sql
CREATE TABLE timetable_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data TEXT,
    hash_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

## Excel File Structure

The API expects Excel files with specific structures:

### Lecture Timetables
- Files should be placed in the `api/drafts/` directory
- Each file should contain multiple sheets for different days
- Column headers represent time slots (e.g., "8:00-9:00")
- Row values contain course information for each time slot

### Exam Timetables
- Files should be placed in the `api/drafts/` directory
- Should contain columns:
  - DATE
  - START
  - END
  - COURSE NAME
  - CLASS
  - LECTURE HALL
  - INVIGILATOR (UPDATED)

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `404 Not Found`: When the requested Excel file doesn't exist
- `500 Internal Server Error`: For processing errors or database connection issues
- `422 Unprocessable Entity`: For validation errors in the request body

Example error response:
```json
{
  "detail": "Timetable file not found: api/drafts/nonexistent.xlsx"
}
```

## Usage Example

To retrieve a lecture timetable for class "EL 3" from "Draft_1.xlsx":

```javascript
const response = await fetch('http://localhost:3000/api/v1/get_time_table', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    filename: 'Draft_1.xlsx',
    class_pattern: 'EL 3',
    is_exam: false
  })
});

const timetable = await response.json();
```

## Available Files

The following timetable files are available in the `api/drafts/` directory:
1. Draft_1.xlsx
2. Draft_1_ex.xlsx
3. Draft_2.xlsx

## Caching

The API uses PostgreSQL for caching processed timetable data. Cached data expires after 1 hour (3600 seconds) to ensure freshness when timetable files are updated.