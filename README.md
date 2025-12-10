# Squadron Scheduler

A comprehensive application for managing flying and simulator schedules, training requirements, and training effectiveness reporting for a USAF bomber squadron.

## Features

- **Schedule Management**: Create, edit, and manage flight and simulator events
- **Pilot Management**: Track pilot profiles, qualifications, and availability
- **Currency Tracking**: Import and track currency requirements from spreadsheets
- **CMR/BMC Status**: Automatically determine pilot Combat Mission Ready (CMR) or Basic Mission Qualification (BMC) status
- **Schedule Optimization**: Optimize pilot assignments based on availability, currency needs, and fairness
- **Calendar Integration**: Export pilot schedules to ICS files for calendar applications
- **Reporting**: Generate reports on flight and simulator events per pilot

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript, Material-UI
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core configuration and utilities
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── alembic/      # Database migrations
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── contexts/
│       ├── pages/
│       └── services/
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker Compose

1. Clone the repository
2. Create a `.env` file in the `backend/` directory:
   ```
   DATABASE_URL=postgresql://squadron_user:squadron_pass@db:5432/squadron_scheduler
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend

1. Navigate to `backend/` directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create `.env` file)
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. Navigate to `frontend/` directory
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## User Roles

- **Admin**: Full access to all features
- **Scheduler**: Can manage schedules, pilots, and events
- **Pilot**: Can view their own schedule and status

## License

[Your License Here]
