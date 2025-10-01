import json
import os

from src.api.main import app

"""
PUBLIC_INTERFACE
Utility script to generate the latest OpenAPI schema into interfaces/openapi.json.
Run this after modifying routes to keep the interface spec up to date.
"""

# PUBLIC_INTERFACE
def write_openapi():
    """Generate and write OpenAPI schema JSON to interfaces/openapi.json."""
    openapi_schema = app.openapi()
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)

if __name__ == "__main__":
    write_openapi()
