# Deployment Strategy

This document outlines the operational deployment lifecycle for the VoxCore API onto the target AWS infrastructure.

## Environment Variables
The application strictly reads sensitive credentials and environment-specific toggles from the `.env` file via the `Configuration` package. 
For the Groq-powered AWS free tier deployment, the following variables must be configured on the production host:

```env
# Server
PORT=8000
ENVIRONMENT=production

# API Keys
GROQ_API_KEY=gsk_your_secure_api_key
```

## Docker Containerization (Planned)
To ensure the application behaves identically on local development laptops and the AWS EC2 instance, the API must be containerized.

### Target `docker-compose.yml` Topology
1. **api-service**: The FastAPI application running via Uvicorn.
2. **redis-cache** *(Optional)*: If the `Memory` package scales beyond in-memory processing.
3. **chromadb** *(Optional)*: Vector database for semantic memory retrieval.

*Note: For the $0 AWS Free Tier deployment (1GB RAM), running Docker introduces overhead. Running the Uvicorn application directly via a `systemd` service or a lightweight process manager (like `pm2` or `supervisor`) is recommended to conserve memory.*

## Continuous Deployment (CI/CD)
Changes merged to the `main` branch should trigger automated checks. 

A standard GitHub Actions workflow should be implemented to:
1. Run Pytest (`uv run pytest`)
2. Lint the codebase (`uv run ruff check`)
3. Validate schema types (`uv run mypy .`)

If the CI pipeline passes, a webhook or deployment script can pull the latest changes onto the EC2 instance and restart the background process.
