# Quick Start Guide

Get the Real Estate AI Platform up and running in seconds!

## 🚀 One-Command Start

### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

### Windows
```cmd
start.bat
```

### Using Make (Linux/macOS)
```bash
make start
```

## 🧪 One-Command Test

### Linux/macOS
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Windows
```cmd
run_tests.bat
```

### Using Make
```bash
make test-cov
```

## 📋 Manual Steps (if scripts don't work)

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Initialize Database
```bash
docker-compose exec backend python init_db.py
```

### 3. (Optional) Seed Mock Data
```bash
# Using Make
make seed

# Or directly
docker-compose exec backend python seed_db.py
```

**See:** [SEED_DATA.md](SEED_DATA.md) for detailed seeding guide.

### 4. Run Tests
```bash
cd backend
pytest --cov=app --cov-report=html tests/
```

## 🎯 Common Commands

### Using Makefile (Recommended)

#### Service Management
```bash
make start       # Start all services and initialize database
make stop        # Stop all services
make restart     # Restart all services
make logs        # View logs from all services
make up          # Start services (docker-compose up -d)
make down        # Stop services (docker-compose down)
```

#### Testing
```bash
make test        # Run all tests
make test-cov    # Run tests with coverage report
make test-watch  # Run tests in watch mode (requires pytest-watch)
```

#### Data Management
```bash
make seed        # Seed database with mock data
make migrate     # Initialize database schema
```

#### Development
```bash
make dev-backend   # Start backend in development mode (hot reload)
make dev-frontend  # Start frontend in development mode (hot reload)
```

#### Build & Cleanup
```bash
make build       # Build all Docker images
make clean       # Clean up containers and volumes
```

**See all commands:**
```bash
make help
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild and start
docker-compose up -d --build
```

### Development Mode

```bash
# Backend (with hot reload)
make dev-backend
# or
cd backend && uvicorn app.main:app --reload

# Frontend (with hot reload)
make dev-frontend
# or
cd frontend/react-app && npm start
```

## 📍 Access Points

Once started, access:
- **Frontend**: http://localhost:3000
- **Gradio UI**: http://localhost:7860
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minio/minio123)
- **Database Viewer (Adminer)**: http://localhost:8081
  - System: PostgreSQL
  - Server: `db`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `realestate`

## 🐛 Troubleshooting

### Docker not running
```bash
# Check Docker status
docker info

# Start Docker Desktop
```

### Ports already in use
```bash
# Check what's using the ports
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Stop conflicting services or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Tests failing
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run tests with verbose output
pytest -v tests/
```

## ⚡ Quick Development Workflow

1. **Start services**: `make start` or `./start.sh`
2. **Run tests**: `make test-cov` or `./run_tests.sh`
3. **Make changes**: Edit code in `backend/app/` or `frontend/react-app/src/`
4. **Test changes**: Tests auto-run or use `make test`
5. **View results**: Check http://localhost:8000/docs for API changes

## 🔄 Full Reset

If something goes wrong:

```bash
# Stop and remove everything
make clean

# Or manually
docker-compose down -v
rm -rf data/postgres data/minio data/uploads

# Start fresh
make start
```

## 📚 Next Steps

- Read [README.md](README.md) for architecture overview
- Check [README-backend.md](README-backend.md) for API details
- See [README-frontend.md](README-frontend.md) for UI development
- Review [README-middleware.md](README-middleware.md) for infrastructure

## 💡 Pro Tips

1. **Use Makefile**: `make` commands are faster and easier
2. **Watch logs**: `make logs` in a separate terminal
3. **Hot reload**: Use `make dev-backend` and `make dev-frontend` for development
4. **Test coverage**: Always check `backend/htmlcov/index.html` after tests
5. **Docker compose**: Use `docker-compose logs -f <service>` for specific service logs

