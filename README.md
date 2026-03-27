# Flask Login Demo with Advanced Docker Compose

A production‑oriented demonstration of a Python Flask login application, containerized with Docker and orchestrated with Docker Compose.  
**This project is intended for testing and educational purposes only** – it showcases advanced Docker features:

- **Network segregation** – public `frontend` + private `backend` (`internal: true`)
- **Healthchecks & dependencies** – PostgreSQL healthcheck, web waits for `service_healthy`
- **Secrets management** – sensitive data injected via Docker secrets
- **Resource limits** – CPU and memory constraints for each service
- **Multiple Compose files** – base, development, production, and tools profiles
- **Watch mode** – live code synchronization during development
- **Named volumes** – persistent data for PostgreSQL and Redis
- **Environment‑based configuration** – separate `.env` files for each profile

---

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
        │   - pgAdmin (optional)      │
        │   - MailHog (optional)      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Docker Network: backend   │   (internal, no internet)
        │   - web container           │
        │   - db container (PostgreSQL)│
        │   - redis (optional)        │
        │   - MailHog (optional)      │
        └─────────────────────────────┘
```

- The **frontend** network is bridged and accessible from the host (port `8080`).
- The **backend** network is marked `internal: true` – containers inside cannot reach the outside world, and no external traffic can reach them.
- The `web` service connects to **both** networks, acting as the only entry point to the database.
- Optional tools (pgAdmin, Redis, MailHog) are activated via profiles.

---

## Prerequisites

- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0
- Git (optional)

---

## Quick Start

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ShellFelipeSilva/flask-login-demo.git
   cd flask-login-demo
   ```

2. **Set up environment variables**  
   Copy the example file and adjust the credentials:
   ```bash
   cp docker/.env.example docker/.env
   ```
   Edit `docker/.env` to your liking (at least set a strong `SECRET_KEY`).

3. **Build and start the services (development mode)**
   ```bash
   cd docker
   docker-compose up -d
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

---

## Advanced Features

### 1. Network Isolation
- **Frontend** network – exposed to host, allows external access.
- **Backend** network – `internal: true`, no inbound/outbound internet traffic.  
  The database lives only on `backend`, the web container is attached to both.

### 2. Healthcheck & Dependency
- PostgreSQL runs a `pg_isready` healthcheck every 10 seconds.
- The web service uses `depends_on: condition: service_healthy`, so it only starts when the database is ready.

### 3. Secrets Management
- Sensitive data (database password, Flask secret key) are stored as Docker secrets.
- Secrets are mounted as files inside containers (`/run/secrets/`), never exposed in environment variables.

### 4. Resource Limits
- CPU and memory limits are defined for each service using `deploy.resources`.
- Example: web is limited to 0.5 CPU and 512 MB memory.

### 5. Multiple Compose Files
- `docker-compose.yml` – base configuration.
- `docker-compose.dev.yml` – development overrides (e.g., hot reload, additional ports).
- `docker-compose.prod.yml` – production optimizations (replicas, restart policies).
- `docker-compose.tools.yml` – optional tools (pgAdmin, Redis, MailHog) with profiles.

### 6. Watch Mode (Development)
- When `docker-compose.dev.yml` is used, the `develop.watch` section enables automatic code synchronization and rebuilds on changes.

### 7. Persistent Volumes
- Named volumes `postgres_data` and `redis_data` ensure data survives container restarts and removals.

### 8. Environment Profiles
- Separate `.env.dev` and `.env.prod` files allow different configurations per environment.

---

## Project Structure

```
.
├── app/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Multi‑stage Docker build
│   └── templates/
│       └── login.html         # Login template
├── docker/
│   ├── docker-compose.yml         # Base configuration
│   ├── docker-compose.dev.yml     # Development overrides
│   ├── docker-compose.prod.yml    # Production overrides
│   ├── docker-compose.tools.yml   # Optional tools
│   ├── .env.example               # Template for environment variables
│   ├── .env.dev                   # Development environment
│   ├── .env.prod                  # Production environment
│   └── secrets/
│       ├── db_password.txt        # Docker secret (example)
│       └── secret_key.txt         # Docker secret (example)
├── .gitignore
└── README.md
```

---

## Usage

### Development (with hot reload and optional tools)

```bash
cd docker
# Copy secrets examples
cp secrets/db_password.txt.example secrets/db_password.txt
cp secrets/secret_key.txt.example secrets/secret_key.txt
# Start with dev profile
docker-compose up -d
```

Access:
- **Application**: [http://localhost:8080](http://localhost:8080)
- **pgAdmin**: [http://localhost:5050](http://localhost:5050) (admin@example.com / admin123)
- **MailHog**: [http://localhost:8025](http://localhost:8025)

### Production

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Optional Tools Only

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.tools.yml --profile tools up -d
```

### Stop and Remove

```bash
cd docker
docker-compose down
```

Remove everything including volumes:
```bash
docker-compose down -v
```

---

## Testing the Setup

### Verify Health Status
```bash
docker inspect $(docker-compose ps -q db) | grep -A 10 Health
```

### Test Network Isolation
- Check backend isolation:
  ```bash
  docker exec $(docker-compose ps -q db) ping 8.8.8.8
  # Expected: Network unreachable
  ```
- Check that the database is not exposed to the host:
  ```bash
  psql -h localhost -p 5432 -U flask_user -d flask_db
  # Expected: connection refused
  ```
- Check connectivity from web to db:
  ```bash
  docker exec $(docker-compose ps -q web) python -c "import socket; socket.gethostbyname('db')"
  ```

### Simulate a Database Failure
Stop PostgreSQL inside the container and watch the health status turn `unhealthy`:
```bash
docker exec $(docker-compose ps -q db) su - postgres -c "pg_ctl stop -D /var/lib/postgresql/data"
docker inspect $(docker-compose ps -q db) | grep -A 10 Health
```

---

## Environment Variables

The following variables can be set in `docker/.env`, `docker/.env.dev`, or `docker/.env.prod`:

| Variable | Description | Default |
|----------|-------------|---------|
| `COMPOSE_PROJECT_NAME` | Docker project name (prefix for containers/volumes) | `flask_login_demo` |
| `DB_USER` | PostgreSQL username | `flask_user` |
| `DB_PASSWORD` | PostgreSQL password (used only if not using secrets) | (required) |
| `DB_NAME` | PostgreSQL database name | `flask_db` |
| `FLASK_ENV` | Flask environment (`development` / `production`) | `production` |
| `WEB_PORT` | Host port for the web application | `8080` |
| `PGADMIN_EMAIL` | pgAdmin login email | `admin@example.com` |
| `PGADMIN_PASSWORD` | pgAdmin password | `admin123` |
| `PGADMIN_PORT` | Host port for pgAdmin | `5050` |
| `MAILHOG_SMTP` | MailHog SMTP port | `1025` |
| `MAILHOG_UI` | MailHog UI port | `8025` |

---

## Security Notes

- The backend network (`internal: true`) provides strong isolation – the database has no internet access and cannot be reached from outside.
- The application runs as a non‑root user inside the container.
- Secrets are stored in Docker secrets, never exposed in environment variables.
- Resource limits prevent a single service from consuming all host resources.
- The image is built with multi‑stage to keep the final image small and avoid build‑time tools in production.

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Disclaimer

**This is a demonstration project intended for testing and learning purposes only.** It is not hardened for production use. Use at your own risk.
