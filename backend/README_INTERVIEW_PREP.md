# Interview Prep Backend API Documentation

This document describes the backend API endpoints for the Interview Preparation feature.

## Table of Contents

1. [Setup](#setup)
2. [Projects API](#projects-api)
3. [Interviews API](#interviews-api)
4. [Search API](#search-api)
5. [Text Refinement API](#text-refinement-api)
6. [Data Models](#data-models)

## Setup

### Environment Variables

Create a `.env` file in the project root with the following API keys:

```bash
# Required for search functionality
TAVILY_API_KEY=your_tavily_api_key_here

# Required for AI features - at least one LLM provider needed
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_PROJECT_ID=your_project_id_here

# Optional alternative LLM provider
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the server
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## Projects API

Manage interview preparation projects.

### Create Project

```http
POST /api/projects
Content-Type: application/json

{
  "title": "My Interview Project"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "My Interview Project",
  "last_modified": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00",
  "stats": {
    "note_count": 0,
    "has_context": false
  }
}
```

### List Projects

```http
GET /api/projects?skip=0&limit=100
```

**Response (200):** Array of project objects (newest first)

### Get Project

```http
GET /api/projects/{project_id}
```

### Update Project

```http
PUT /api/projects/{project_id}
Content-Type: application/json

{
  "title": "Updated Title"
}
```

### Delete Project

```http
DELETE /api/projects/{project_id}
```

**Response (204):** No content. Cascades to all interviews, notes, and canvas blocks.

## Interviews API

Manage interview workspaces with notes and outline canvas.

### Create Interview

```http
POST /api/interviews
Content-Type: application/json

{
  "project_id": 1,
  "interview_title": "Interview with John Doe",
  "background_context": "John is an AI researcher specializing in NLP",
  "notes": [
    {
      "title": "Research Background",
      "order_index": 0,
      "items": [
        {
          "type": "text",
          "content": "Published 15 papers on transformer models",
          "provenance": "web",
          "source_title": "Google Scholar Profile",
          "source_domain": "scholar.google.com",
          "order_index": 0
        }
      ]
    }
  ],
  "canvas_blocks": [
    {
      "type": "heading",
      "text": "Introduction",
      "order_index": 0
    },
    {
      "type": "paragraph",
      "text": "Welcome John and introduce the podcast",
      "order_index": 1
    }
  ]
}
```

**Response (201):** Full interview object with all nested data

### Get Interview

```http
GET /api/interviews/{interview_id}
```

Returns complete interview with all notes (including items) and canvas blocks.

### Update Interview Metadata

```http
PUT /api/interviews/{interview_id}
Content-Type: application/json

{
  "interview_title": "Updated Title",
  "background_context": "Updated context"
}
```

### Autosave Interview

Full replacement of interview state. Deletes existing notes/blocks and recreates from payload.

```http
POST /api/interviews/{interview_id}/autosave
Content-Type: application/json

{
  "interview_title": "Current Title",
  "background_context": "Current context",
  "notes": [...],
  "canvas_blocks": [...]
}
```

**Use case:** Frontend periodic autosave, final save before closing.

### Delete Interview

```http
DELETE /api/interviews/{interview_id}
```

**Response (204):** Cascades to notes and canvas blocks.

## Search API

Web search with AI-generated summaries.

### Perform Search

```http
POST /api/search
Content-Type: application/json

{
  "query": "latest developments in large language models",
  "llm_provider": "openai",
  "background_context": "Interviewing an AI researcher about LLMs"
}
```

**Parameters:**
- `query` (required): Search query string
- `llm_provider` (optional): `"openai"` or `"deepseek"` (default: `"openai"`)
- `background_context` (optional): Interview context for more relevant summaries

**Response (200):**
```json
{
  "summary": "Recent developments in large language models include... [1] [2]",
  "citations": [
    {
      "number": 1,
      "title": "GPT-4 Technical Report",
      "url": "https://arxiv.org/..."
    }
  ],
  "web_results": [
    {
      "title": "Latest LLM Research",
      "url": "https://...",
      "snippet": "Key findings from recent studies...",
      "domain": "arxiv.org"
    }
  ],
  "image_results": [
    {
      "url": "https://...",
      "thumbnail_url": "https://...",
      "title": null,
      "source_url": null
    }
  ]
}
```

**Usage Flow:**
1. User searches for information
2. Backend calls Tavily API for web results and images
3. Backend generates AI summary with citations using selected LLM
4. Frontend displays summary, results, and images
5. User can "Add to Note" to save snippets or images

## Text Refinement API

AI-powered text refinement for canvas blocks.

### Refine Text

```http
POST /api/canvas/refine
Content-Type: application/json

{
  "block_id": 42,
  "action": "improve",
  "llm_provider": "openai"
}
```

**Parameters:**
- `block_id` (required): ID of canvas block to refine
- `action` (required): One of:
  - `"improve"`: Enhance clarity and professionalism
  - `"shorten"`: Reduce length (~55% of original)
  - `"change_tone"`: Make conversational for podcast
- `llm_provider` (optional): `"openai"` or `"deepseek"` (default: `"openai"`)

**Response (200):**
```json
{
  "original_text": "This is the original text from the canvas block.",
  "refined_text": "This is the improved version with better clarity.",
  "action": "improve"
}
```

**Usage Flow:**
1. User selects text in canvas
2. Clicks refinement action (Improve/Shorten/Change Tone)
3. Backend retrieves block, applies LLM transformation
4. Frontend shows original and refined versions
5. User can accept or reject changes

## Data Models

### Project
- `id`: Integer (auto-generated)
- `title`: String (1-500 chars, required)
- `last_modified`: DateTime (auto-updated)
- `created_at`: DateTime (auto-set)
- `stats`: Object with `note_count` and `has_context`

### Interview
- `id`: Integer (auto-generated)
- `project_id`: Integer (required, foreign key)
- `interview_title`: String (1-500 chars, required)
- `background_context`: String (0-50000 chars, optional)
- `timestamp`: DateTime (auto-set)
- `notes`: Array of Note objects
- `canvas_blocks`: Array of CanvasBlock objects

### Note
- `id`: Integer (auto-generated)
- `title`: String (1-500 chars, required)
- `order_index`: Integer (≥0, for drag-drop ordering)
- `created_at`: DateTime (auto-set)
- `items`: Array of NoteItem objects

### NoteItem
- `id`: Integer (auto-generated)
- `type`: Enum (`"text"` or `"image"`)
- `content`: String (1-50000 chars, text or image URL)
- `provenance`: Enum (`"web"` or `"manual"`)
- `source_title`: String (optional, for web items)
- `source_domain`: String (optional, for web items)
- `order_index`: Integer (≥0)
- `created_at`: DateTime (auto-set)

### CanvasBlock
- `id`: Integer (auto-generated)
- `type`: Enum (`"heading"` or `"paragraph"`)
- `text`: String (1-50000 chars, required)
- `order_index`: Integer (≥0)
- `created_at`: DateTime (auto-set)

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST (resource created)
- `204 No Content`: Successful DELETE
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error (invalid input)
- `500 Internal Server Error`: Server error (API failures, etc.)

Error response format:
```json
{
  "detail": "Human-readable error message"
}
```

## Testing

Run the test suite:

```bash
# Run all interview prep tests
pytest backend/tests/test_interview_models.py \
       backend/tests/test_interview_schemas.py \
       backend/tests/test_projects_api.py \
       backend/tests/test_interviews_api.py -v

# Run all tests
pytest backend/tests/ -v
```

Current test coverage:
- Models: 7 tests
- Schemas: 22 tests
- Projects API: 14 tests
- Interviews API: 11 tests
- **Total: 54 tests, all passing**

## Notes

### Performance
- Search API: Typically < 5 seconds (includes Tavily + LLM)
- Text Refinement: Typically < 3 seconds (LLM only)
- Interview autosave: Optimized with joinedload for nested data

### Rate Limiting
External API calls are subject to provider rate limits:
- Tavily: Check your plan limits
- OpenAI: Based on API key tier
- DeepSeek: Based on API key tier

Consider implementing caching for frequently searched queries.

### Ordering
All ordered entities (notes, items, blocks) use `order_index`:
- Frontend manages ordering via drag-and-drop
- Backend preserves order on save/load
- Order is maintained in query results via SQLAlchemy `order_by`
