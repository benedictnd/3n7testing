# 3&7 Training Platform

A comprehensive sports training management system designed for Southeast Asia, with special considerations for Indonesian athletes and coaches.

## Features

- **Integrated Training System**
  - Real-time session tracking
  - Performance analytics
  - Mobile-responsive calendar
  - Multi-language support (English, Bahasa Indonesia)

- **Independent Training Module**
  - Self-paced training programs
  - Progress tracking
  - Feedback submission
  - Equipment management

- **Regional Optimizations**
  - Bandwidth-optimized data flow
  - Heat-resistant touch handling
  - Data sovereignty compliance
  - Cultural adaptations (e.g., Ramadan timing)

## Technical Stack

- **Frontend**: Next.js, TypeScript, TailwindCSS  
- **Backend**: Python (FastAPI)  
- **Database**: Supabase (PostgreSQL)  
- **Authentication**: Supabase Auth  
- **Deployment**: Vercel (frontend), Railway/Fly.io/Render (backend – optional)  

## Getting Started

## Repository

This project is hosted at: [https://github.com/benedictnd/3n7testing](https://github.com/benedictnd/3n7testing)

## Local Deployment (with Docker)

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/benedictnd/3n7testing.git
   cd 3n7testing
   ```

2. **(Optional) Configure environment variables:**
   - Copy and edit `.env.example` as needed for your local setup.

3. **Build and start all services:**
   ```bash
   docker-compose up --build -d
   ```
   This will start:
   - Backend (FastAPI, auto-reloads on code changes)
   - Frontend (Next.js, auto-reloads on code changes)
   - PostgreSQL & Redis
   - Redocly API docs (serving OpenAPI schema)

4. **Access the app and docs:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc (FastAPI): [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Redocly Standalone: [http://localhost:8080](http://localhost:8080)

5. **Update OpenAPI schema after backend changes:**
   ```bash
   docker-compose exec backend python export_openapi.py
   ```
   This regenerates `backend/openapi.json` for the Redocly docs service.

---

For more details, see [`docs/openapi.md`](docs/openapi.md).

     npm run dev
     ```

   - **Backend**:
     ```bash
     uvicorn main:app --reload
     ```

## Development Guidelines

- Follow TypeScript and Python best practices
- Use functional React components with hooks
- Maintain modular and reusable FastAPI endpoints
- Implement proper error handling and logging
- Write unit/integration tests for key features
- Follow the established code style guide

## Security

- All commits must be signed
- Regular dependency and codebase audits
- PDPA & regional data protection compliance
- Data stored within Southeast Asia via Supabase
- Periodic penetration testing and monitoring

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request
4. Ensure all tests pass
5. Get code review approval

## License

Proprietary – All rights reserved

## Support

For support, please contact the development team or raise an issue in the repository.

