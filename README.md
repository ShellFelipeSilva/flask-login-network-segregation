# Flask Login Demo with Docker Compose – Network Isolation & Healthchecks

A minimal, production‑oriented demonstration of a Python Flask login application, containerized with Docker and orchestrated with Docker Compose.  
**This project is intended for testing and educational purposes only** – it showcases advanced Docker concepts such as:

- **Network segregation** (public frontend network + private backend network with `internal: true`)
- **Healthchecks** and service dependencies (`condition: service_healthy`)
- **Multi‑stage Docker builds** with a non‑root user
- **Persistent volumes** for PostgreSQL
- **Environment‑based configuration** via `.env` files

## Architecture

```
           ┌───────────────────────┐
           │       Host            │
           │  http://localhost:8080│
           └───────────┬───────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Docker Network: frontend  │   (public, external access)
        │   - web container           │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Docker Network: backend   │   (internal, no internet)
        │   - web container           │
        │   - db container (PostgreSQL)│
        └─────────────────────────────┘
```

- The **frontend** network is bridged and accessible from the host (port `8080`).
- The **backend** network is marked `internal: true` – containers inside cannot reach the outside world, and no external traffic can reach them.
- The `web` service connects to **both** networks, acting as the only entry point to the database.
- The `db` service lives **only** on the backend network, completely isolated from the host and the internet.

## Prerequisites

- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0
- Git (optional)

## Quick Start

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/flask-login-demo.git
   cd flask-login-demo
   ```

2. **Set up environment variables**  
   Copy the example file and adjust the credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to your liking (at least set a strong `SECRET_KEY`).

3. **Build and start the services**  
   ```bash
   docker-compose up -d --build
   ```

4. **Initialize the database** (creates tables and test users)  
   ```bash
   docker-compose exec web flask init-db
   ```

5. **Access the application**  
   Open your browser at [http://localhost:8080](http://localhost:8080)  
   Use the following test credentials:
   - `admin` / `admin123` (role: admin)
   - `joao` / `joao123` (role: user)
   - `maria` / `maria123` (role: user)

## Project Structure

```
.
├── app/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Multi‑stage Docker build
│   └── templates/
│       └── login.html         # Minimal login template
├── docker-compose.yml         # Orchestration with networks & healthchecks
├── .env.example               # Template for environment variables
├── .gitignore
└── README.md
```

## How It Works – Key Concepts

### 1. Network Isolation
- `frontend` – public, mapped to host port 8080.
- `backend` – internal, no external access.  
  The `web` container is attached to both, allowing it to serve public requests while still reaching the database.

### 2. Healthcheck & Dependency
- The `db` service runs a `pg_isready` healthcheck every 10 seconds.
- The `web` service uses `depends_on: condition: service_healthy`, so it will not start until the database is fully ready.

### 3. Multi‑stage Dockerfile
- **Stage 1 (builder)** installs dependencies into a temporary image.
- **Stage 2 (final)** copies only the necessary files and runs as a non‑root user (`appuser`), reducing the attack surface.

### 4. Persistent Data
- PostgreSQL data is stored in a named volume `postgres_data`, surviving container restarts and removals.

### 5. Environment Variables
- Sensitive data (database credentials, secret key) are injected via `.env` – never hardcoded.

## Testing the Setup

### Verify Health Status
```bash
docker inspect <db_container_id> | grep -A 10 Health
```

### Test Network Isolation
- Check backend isolation:  
  ```bash
  docker exec -it <db_container_id> ping 8.8.8.8
  # Expected: Network unreachable
  ```
- Check that the database is not exposed to the host:  
  ```bash
  psql -h localhost -p 5432 -U felipe -d login_db
  # Expected: connection refused
  ```
- Check connectivity from web to db:  
  ```bash
  docker exec -it <web_container_id> python -c "import socket; socket.gethostbyname('db')"
  ```

### Simulate a Database Failure
- Stop PostgreSQL inside the container and watch the health status turn `unhealthy`.

## Cleaning Up

- Stop and remove containers, networks, but keep volumes:  
  ```bash
  docker-compose down
  ```
- Remove everything including volumes (data loss!):  
  ```bash
  docker-compose down -v
  ```

## Security Notes

- The backend network (`internal: true`) is a strong isolation layer – the database has no internet access and cannot be reached from outside.
- The application runs as a non‑root user inside the container.
- All secrets are stored in environment variables; for production consider using Docker Secrets or a vault.
- The image is built with multi‑stage to keep the final image small and avoid build‑time tools in production.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Disclaimer

**This is a demonstration project intended for testing and learning purposes only.** It is not hardened for production use. Use at your own risk.
