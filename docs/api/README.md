# API Documentation

This directory contains comprehensive documentation for the Sports Game Tracker API.

## Files

### `openapi-schema.json`
OpenAPI 3.0 schema file that can be imported into:
- Postman
- Insomnia
- Swagger UI
- Any OpenAPI-compatible tool

**To regenerate:**
```bash
python scripts/generate_api_schema.py
```

### `API_DOCUMENTATION.md`
Complete API documentation including:
- Endpoint descriptions
- Request/response examples
- Query parameters
- Filtering and searching
- Code examples (Python, JavaScript, cURL)
- Use cases

## Interactive Documentation

The API includes built-in interactive documentation:

- **Swagger UI:** http://localhost:8000/api/docs/
  - Try out endpoints directly in the browser
  - See request/response schemas
  - Test authentication
  
- **ReDoc:** http://localhost:8000/api/redoc/
  - Clean, responsive documentation
  - Three-column layout
  - Search functionality

- **OpenAPI Schema:** http://localhost:8000/api/schema/
  - Raw JSON schema
  - Download for offline use

## Quick Start

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Visit the API root:**
   ```
   http://localhost:8000/api/
   ```

3. **Explore endpoints in Swagger UI:**
   ```
   http://localhost:8000/api/docs/
   ```

4. **Import schema into Postman:**
   - Open Postman
   - Click Import
   - Select `openapi-schema.json`
   - Start making requests!

## API Endpoints

- `GET /api/leagues/` - List all leagues
- `GET /api/teams/` - List all teams
- `GET /api/games/` - List all games
- `GET /api/games/live/` - Get live games
- `GET /api/games/today/` - Get today's games
- `GET /api/players/` - List all players
- `GET /api/scores/` - List all period scores

## Features

- **Filtering:** Filter results by various fields
- **Searching:** Full-text search on names and descriptions
- **Ordering:** Sort results by any field
- **Pagination:** 20 items per page (configurable)
- **Nested Data:** Related objects included in responses
- **Custom Actions:** Special endpoints for common queries

## Schema Documentation

The API uses drf-spectacular to generate OpenAPI 3.0 schemas. Key features:

- Automatic schema generation from Django models and serializers
- Comprehensive parameter documentation
- Request/response examples
- Tag-based organization
- Reusable component schemas

## For Developers

### Adding New Endpoints

1. Create serializer in `apps/api/serializers.py`
2. Create viewset in `apps/api/viewsets.py`
3. Add docstrings and `@extend_schema` decorators
4. Register in `apps/api/urls.py`
5. Regenerate schema: `python scripts/generate_api_schema.py`

### Documenting Endpoints

Use drf-spectacular decorators:

```python
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

@extend_schema_view(
    list=extend_schema(
        summary="List resources",
        description="Detailed description here",
        tags=["resource"],
        parameters=[
            OpenApiParameter(
                name="filter",
                type=OpenApiTypes.STR,
                description="Filter description"
            ),
        ],
    ),
)
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet docstring."""
    pass
```

### Customizing Schema

Edit `config/settings/base.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API Title',
    'DESCRIPTION': 'Your API description',
    'VERSION': '1.0.0',
    # ... more settings
}
```

## Testing

Test API endpoints:

```bash
# Run API tests
pytest apps/api/tests/

# Test with coverage
pytest apps/api/tests/ --cov=apps.api
```

## Production Considerations

Before deploying to production:

1. Add authentication (API keys, OAuth2, JWT)
2. Implement rate limiting
3. Add CORS headers for frontend
4. Use HTTPS only
5. Set up monitoring and logging
6. Cache frequently accessed endpoints
7. Add API versioning

## Support

For questions or issues:
- Check the documentation at http://localhost:8000/api/docs/
- Review examples in `API_DOCUMENTATION.md`
- Consult the OpenAPI schema
- Contact support@sportsgametracker.com
