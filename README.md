# 3&7 Training & Recovery Platform

A comprehensive platform for managing training sessions, tracking athlete progress, and generating reports.

## Features

- **User Management**: Create and manage different user roles (Athletes, Coaches, Stakeholders, Support Staff)
- **Training Sessions**: Schedule and manage training sessions
- **Attendance Tracking**: Track athlete attendance at training sessions
- **Feedback Collection**: Collect and analyze feedback from athletes
- **Reporting System**: Generate comprehensive reports on training, attendance, and feedback

## Project Structure

The project is split into a backend API built with FastAPI and a frontend application built with Next.js.

### Backend

The backend is built with FastAPI and SQLAlchemy, providing a RESTful API for the frontend to consume.

- `main.py`: Main application entry point
- `routes/`: API endpoints
- `models/`: Pydantic models for validation and SQL models for the database
- `services/`: Business logic for the application
- `dependencies/`: Reusable dependencies for the API

### Frontend

The frontend is built with Next.js and uses React for the UI components.

- `pages/`: Next.js pages
- `components/`: Reusable React components
- `lib/`: Utility functions and API client

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL

### Backend Setup

1. Create a virtual environment and activate it:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/training_platform
SECRET_KEY=your-super-secret-key-for-development-only
ENVIRONMENT=development
PORT=8000
```

4. Run database migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

5. Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:

```bash
npm run dev
```

## Running Both Together

You can use the provided `run-dev.sh` script to run both the backend and frontend together:

```bash
# Make the script executable
chmod +x run-dev.sh

# Run the script
./run-dev.sh
```

## API Documentation

When the backend is running, you can access the automatic API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## User Roles

The platform supports different user roles, each with specific permissions:

- **Athletes**: Can view their own training sessions, mark attendance, and provide feedback
- **Coaches**: Can create and manage training sessions, view athlete information, and generate reports
- **Stakeholders**: Can view training data and reports for athletes
- **Support Staff**: Can provide specialized support to athletes and coaches
- **Administrators**: Have full access to all features of the platform

## Tech Stack

- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **UI Components**: Shadcn UI (based on Radix UI)
- **Form Handling**: React Hook Form with Zod validation
- **Styling**: TailwindCSS

## Getting Started

### Prerequisites

- Node.js 16.8.0 or later
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/training-management-system.git
   cd training-management-system
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

```
training-management-system/
├── app/                    # Next.js app directory
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/             # React components
│   ├── forms/              # Form components
│   │   ├── FeedbackForm.tsx
│   │   ├── RegistrationForm.tsx
│   │   └── TrainingSessionForm.tsx
│   └── ui/                 # UI components (Shadcn)
├── lib/                    # Utility functions
│   └── utils.ts            # Helper functions
├── public/                 # Static assets
├── .gitignore
├── next.config.js
├── package.json
├── README.md
├── tailwind.config.js
└── tsconfig.json
```

## Form Components

### Registration Form

The registration form allows users to sign up with different roles:

- **Athletes**: Can provide information about their sports, experience level, and goals
- **Coaches**: Can specify their specializations, experience, and certifications
- **Stakeholders**: Can indicate their organization, role, and areas of interest
- **Support Staff**: Can detail their specialization, qualifications, and availability

### Training Session Form

The training session form allows coaches to create comprehensive training sessions with:

- Basic session information (title, type, date, time, location)
- Warming up phase details
- Main training phase with exercises, intensity, and duration
- Cooling down phase details
- Target audience selection

### Feedback Form

The feedback form allows athletes to provide detailed feedback on training sessions:

- Overall session rating
- Physical aspects (difficulty, fatigue, pain areas)
- Technical aspects (difficulty, improvements, challenges)
- Mental aspects (difficulty, concentration, motivation)
- Overall enjoyment and willingness to repeat

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Next.js](https://nextjs.org/)
- [React](https://reactjs.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Shadcn UI](https://ui.shadcn.com/)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://github.com/colinhacks/zod) 