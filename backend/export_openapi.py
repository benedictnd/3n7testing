import sys
from fastapi.openapi.utils import get_openapi
from main import app

if __name__ == "__main__":
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    import json
    with open("openapi.json", "w") as f:
        json.dump(schema, f, indent=2)
    print("OpenAPI schema exported to openapi.json")
