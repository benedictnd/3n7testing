# OpenAPI Schema for 3&7 Training Platform API

This document describes how to access and use the OpenAPI schema for the backend FastAPI service. The OpenAPI schema defines the available endpoints, request/response formats, and authentication for the API.

## Accessing the OpenAPI Schema

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Redocly Standalone Docs:** [http://localhost:8080](http://localhost:8080)
- **Raw OpenAPI JSON:** [backend/openapi.json](../backend/openapi.json)

## Updating the OpenAPI Schema

The OpenAPI schema is generated automatically from the FastAPI backend. To update the schema after making changes to your API:

1. Make sure your backend Docker container is running.
2. Run the following command to regenerate the OpenAPI schema inside the backend container:
   ```sh
   docker-compose exec backend python export_openapi.py
   ```
3. The schema will be saved as `backend/openapi.json` and automatically served by the Redocly docs service.

## Redocly API Documentation

The Redocly docs service is configured in `docker-compose.yml` and serves the OpenAPI schema at [http://localhost:8080](http://localhost:8080) for easy sharing and viewing.

---

For more details on the API endpoints, see the [Swagger UI](http://localhost:8000/docs) or [Redoc UI](http://localhost:8000/redoc) provided by FastAPI.
