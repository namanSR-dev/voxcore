# Deployment Strategy

This document outlines the operational deployment lifecycle for the VoxCore API onto the target Oracle OCI infrastructure.

## Environment Variables
The application strictly reads sensitive credentials and environment-specific toggles from the `.env` file via the `Configuration` package. 
For the Groq-powered Oracle free tier deployment, the following variables must be configured on the production host:

```env
# Server
PORT=8000
ENVIRONMENT=production

# API Keys
GROQ_API_KEY=gsk_your_secure_api_key
```

## Docker Containerization
To ensure the application behaves identically on local development laptops and the Oracle OCI instance, the API must be containerized.

### Target `docker-compose.yml` Topology
1. **api-service**: The FastAPI application running via Uvicorn.
2. **redis-cache** *(Optional)*: If the `Memory` package scales beyond in-memory processing.
3. **chromadb** *(Optional)*: Vector database for semantic memory retrieval.

*Note: Unlike traditional 1GB Free Tiers, the Oracle OCI A1 instance provides 24GB of RAM, making it perfectly safe to run multiple Docker containers (including memory-heavy databases like PostgreSQL and Redis) alongside the main API without risk of OOM errors.*

## Continuous Deployment (CI/CD)
Changes merged to the `main` branch should trigger automated checks. 

A standard GitHub Actions workflow should be implemented to:
1. Run Pytest (`uv run pytest`)
2. Lint the codebase (`uv run ruff check`)
3. Validate schema types (`uv run mypy .`)

If the CI pipeline passes, a webhook or deployment script can pull the latest changes onto the Oracle OCI instance and restart the Docker containers.
