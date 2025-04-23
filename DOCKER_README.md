# Docker Setup for 3&7 Training Platform

This document provides instructions for running the 3&7 Training Platform using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Services

The Docker Compose setup includes:

1. **Frontend**: Next.js application
2. **Backend**: FastAPI application
3. **PostgreSQL**: Database for storing application data
4. **Redis**: Cache for improved performance

## Getting Started

### 1. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to customize settings if needed.

### 2. Build and Start Services

```bash
docker-compose up -d
```

To build without cache:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### 3. Access the Applications

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 5. Stop the Services

```bash
docker-compose down
```

To remove volumes (data will be lost):

```bash
docker-compose down -v
```

## Development Workflow

The development environment is configured with hot-reloading:

- Frontend changes will automatically refresh in the browser
- Backend changes will trigger automatic restart of the FastAPI server

## Database Management

### Connect to PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d training_db
```

### Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Reset Database

To recreate the database from scratch:

```bash
docker-compose down -v
docker-compose up -d
```

## Redis CLI

Connect to Redis CLI:

```bash
docker-compose exec redis redis-cli
```

## Troubleshooting

### Frontend Issues

If the frontend fails to start or connect to the backend:

```bash
docker-compose restart frontend
```

### Backend Issues

If the backend fails to start or connect to the database:

```bash
docker-compose restart backend
```

### Database Connection Issues

```bash
docker-compose restart postgres
```

### Redis Connection Issues

```bash
docker-compose restart redis
``` 