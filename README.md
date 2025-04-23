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

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/3n7-training-platform.git
   cd 3n7-training-platform
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```

5. Run development servers:

   - **Frontend**:
     ```bash
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

