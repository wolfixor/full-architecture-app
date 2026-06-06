# Task API

A simple task management API built with clean architecture principles, suitable for learning infrastructure deployment on Kubernetes.

## Architecture Overview

This project follows a simple, production-ready structure similar to established Python projects:

```
app/
├── api/              # API endpoints and routing
│   ├── endpoints/    # Individual endpoint modules
│   │   ├── health.py # Health/readiness endpoints
│   │   └── tasks.py  # Task management endpoints
│   └── api.py       # Main API router configuration
├── core/            # Core application modules
│   ├── config.py    # Configuration management
│   └── logger.py    # Structured logging setup
├── models/          # Data models (Pydantic)
│   └── task.py      # Task data models
├── services/        # Business logic services
│   └── task_service.py # Task business logic
└── main.py         # Application entry point
```

## Features

- RESTful API with CRUD operations for tasks
- Health (`/health`) and readiness (`/ready`) endpoints
- Structured logging
- Environment variable configuration
- Graceful shutdown
- Docker containerization
- Multi-stage Docker build



### Docker

1. Build the image:
```bash
docker build -t task-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 task-api
```

## API Endpoints

- `GET /health` - Health check for liveness probes
- `GET /ready` - Readiness check for readiness probes
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

## Sample Requests

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/api/ready

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to Kubernetes", "description": "Set up k3s cluster and deploy the app"}'

# List all tasks
curl http://localhost:8000/api/tasks

# Get a specific task
curl http://localhost:8000/api/tasks/{id}

# Update a task
curl -X PUT http://localhost:8000/api/tasks/{id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "status": "in_progress"}'

# Delete a task
curl -X DELETE http://localhost:8000/api/tasks/{id}
```

> Valid status values: `pending`, `in_progress`, `completed`, `cancelled`

## Kubernetes Deployment

See the Kubernetes manifests in the `k8s/` directory for deployment to Kubernetes.

## Project Evolution Path

This project is designed to evolve incrementally:

1. **Phase 1** (Current): Simple monolith with in-memory storage
2. **Phase 2**: Add PostgreSQL for persistence
3. **Phase 3**: Add Redis for caching
4. **Phase 4**: Split into microservices
5. **Phase 5**: Add message queue (Kafka/RabbitMQ)
6. **Phase 6**: Add authentication/authorization
7. **Phase 7**: Add monitoring and observability

## Design Decisions

- **Clean Architecture**: Separates concerns and allows easy swapping of components
- **In-Memory Storage**: Simplest possible storage for initial phase
- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **Pydantic**: Type-safe data validation and serialization
- **Multi-stage Docker**: Optimizes image size and security
- **Non-root user**: Security best practice in Docker container

the flow:
https://chatgpt.com/c/6a217d3e-22b4-83eb-943a-008bd0ec8fa7