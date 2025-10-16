#!/usr/bin/env python
"""
Script to generate OpenAPI schema and save it to a file.
This file can be imported into Postman, Insomnia, or other API clients.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from drf_spectacular.generators import SchemaGenerator

def generate_schema():
    """Generate OpenAPI schema and save to file."""
    generator = SchemaGenerator(title='Sports Game Tracker API')
    schema = generator.get_schema(request=None, public=True)
    
    # Save as JSON
    schema_dir = project_root / 'docs' / 'api'
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = schema_dir / 'openapi-schema.json'
    with open(json_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ OpenAPI schema generated successfully!")
    print(f"📁 Location: {json_path}")
    print(f"📊 Endpoints: {len([p for paths in schema.get('paths', {}).values() for p in paths])}")
    print(f"📝 Schemas: {len(schema.get('components', {}).get('schemas', {}))}")
    print("\n🔧 Import this file into:")
    print("   - Postman: Import > Upload Files")
    print("   - Insomnia: Import/Export > Import Data > From File")
    print("   - SwaggerUI: Any OpenAPI 3.0 compatible tool")
    print(f"\n🌐 Or view documentation at:")
    print(f"   - Swagger UI: http://localhost:8000/api/docs/")
    print(f"   - ReDoc: http://localhost:8000/api/redoc/")
    print(f"   - Schema JSON: http://localhost:8000/api/schema/")

if __name__ == '__main__':
    generate_schema()
