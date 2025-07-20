# Automation & Engagement API Endpoints

This document lists all the new API endpoints added for the advanced automation and engagement features.

## Base URL
All automation endpoints are prefixed with `/api/v1/automation/`

## Authentication
All endpoints require Bearer token authentication via the `Authorization` header.

## Direct Messaging Endpoints

### Campaign Management
- `POST /automation/direct-messages` - Create a new DM campaign
- `GET /automation/direct-messages` - List DM campaigns with filters
- `GET /automation/direct-messages/{campaign_id}` - Get specific campaign
- `PUT /automation/direct-messages/{campaign_id}` - Update campaign
- `DELETE /automation/direct-messages/{campaign_id}` - Delete campaign

### Analytics & Logs
- `GET /automation/direct-messages/stats` - Get DM statistics
- `GET /automation/direct-messages/logs` - Get sending logs with filters

### Batch Operations
- `POST /automation/direct-messages/batch` - Create multiple campaigns

## Comment Management Endpoints

### Comment Processing
- `POST /automation/comments` - Process new comment with AI analysis
- `GET /automation/comments` - List comments with filters
- `GET /automation/comments/{comment_id}` - Get specific comment
- `PUT /automation/comments/{comment_id}` - Update comment status/action

### Analytics & Bulk Operations
- `GET /automation/comments/stats` - Get comment management statistics
- `POST /automation/comments/bulk-process/{social_account_id}` - Bulk process pending comments

## Moderation Endpoints

### Rule Management
- `POST /automation/moderation/rules` - Create moderation rule
- `GET /automation/moderation/rules` - List moderation rules
- `GET /automation/moderation/rules/{rule_id}` - Get specific rule
- `PUT /automation/moderation/rules/{rule_id}` - Update rule
- `DELETE /automation/moderation/rules/{rule_id}` - Delete rule

### Templates & Batch Operations
- `POST /automation/moderation/rules/templates` - Create template rules
- `POST /automation/moderation/rules/batch` - Create multiple rules

### Logs & Analytics
- `GET /automation/moderation/logs` - Get moderation action logs
- `GET /automation/moderation/stats` - Get moderation statistics

## Configuration Endpoints

### Automation Settings
- `GET /automation/config` - Get automation configuration
- `POST /automation/config` - Create automation configuration
- `PUT /automation/config` - Update automation configuration
- `GET /automation/config/all` - List all user configurations

### Feature Controls
- `POST /automation/toggle/{feature}` - Toggle specific automation feature

## Dashboard & Analytics Endpoints

### Overview
- `GET /automation/dashboard` - Get comprehensive automation dashboard
- `GET /automation/health` - Get automation system health check
- `GET /automation/insights` - Get automation insights and recommendations

## Query Parameters

### Common Filters
- `page` - Page number for pagination (default: 1)
- `size` - Items per page (default: 20, max: 100)
- `social_account_id` - Filter by social account
- `is_active` - Filter by active status

### DM Specific
- `message_type` - Filter by message type (welcome, follow_up, etc.)
- `status` - Filter by sending status

### Comment Specific
- `needs_attention` - Filter comments needing attention
- `is_spam` - Filter spam comments
- `is_processed` - Filter processed comments
- `sentiment` - Filter by sentiment (positive, negative, neutral)

### Moderation Specific
- `content_type` - Filter by content type (comment, post, live_stream)
- `action` - Filter by moderation action taken
- `is_automated` - Filter automated vs manual actions
- `days` - Time range for logs/stats (default: 30)

## Response Formats

### Success Responses
All endpoints return JSON responses with appropriate HTTP status codes:
- `200 OK` - Successful retrieval
- `201 Created` - Successful creation
- `204 No Content` - Successful deletion

### Error Responses
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors

### Example Response Structure
```json
{
  "id": 1,
  "user_id": 1,
  "social_account_id": 1,
  "message_type": "welcome",
  "message_content": "Welcome to our community!",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting
- API calls are subject to rate limiting based on user configuration
- Default limits: 1000 requests per hour per user
- Automation features respect their own rate limits (e.g., DMs per hour)

## Webhooks (Future Enhancement)
The API is designed to support webhook notifications for:
- New comments requiring attention
- Moderation actions taken
- DM campaign completions
- System alerts and health issues

## OpenAPI Documentation
Complete interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`