# Troubleshooting Guide

Common issues and solutions for the Real Estate AI Platform.

## Docker Compose Issues

### Error: `.env` file not found

**Problem:**
```
env file C:\code\rn-ai\advanced-real-estate-0.01\.env not found
```

**Solution:**
The `.env` file is optional. Docker Compose will work without it since all required environment variables are set in `docker-compose.yml`.

1. **Option 1: Create empty `.env` file**
   ```bash
   # On Windows
   echo. > .env
   
   # On Linux/Mac
   touch .env
   ```

2. **Option 2: Copy from example**
   ```bash
   cp .env.example .env
   ```

3. **Option 3: Ignore the warning** (it's harmless if all variables are in docker-compose.yml)

### Services not starting

**Check service status:**
```bash
docker-compose ps
```

**View logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs gradio
```

**Restart services:**
```bash
docker-compose restart
# or
make restart
```

## Frontend Connection Issues

### ERR CONNECTION REFUSED on Frontend

**Problem:** Frontend can't connect to backend API.

**Solutions:**

1. **Check if services are running:**
   ```bash
   docker-compose ps
   ```
   All services should show "Up" status.

2. **Check backend is accessible:**
   ```bash
   curl http://localhost:8000/api/health
   # or
   curl http://localhost:8000/
   ```

3. **Check frontend container logs:**
   ```bash
   docker-compose logs frontend
   ```

4. **Rebuild frontend (if Tailwind wasn't installed):**
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

5. **Check nginx configuration:**
   The nginx proxy should forward `/api` requests to `http://backend:8000/api`

6. **Verify API URL in React app:**
   Check `frontend/react-app/src/api.js`:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
   ```

### Frontend shows blank page

**Solutions:**

1. **Check browser console for errors**
2. **Check if React app built successfully:**
   ```bash
   docker-compose logs frontend | grep -i error
   ```

3. **Rebuild frontend:**
   ```bash
   docker-compose build frontend --no-cache
   docker-compose up -d frontend
   ```

### Tailwind CSS not working

**Problem:** Styles not applying after adding Tailwind.

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd frontend/react-app
   npm install
   ```

2. **Rebuild frontend:**
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

3. **Check Tailwind config:**
   Verify `tailwind.config.js` has correct content paths:
   ```javascript
   content: [
     "./src/**/*.{js,jsx,ts,tsx}",
   ],
   ```

## Backend Issues

### Database connection errors

**Problem:** Backend can't connect to PostgreSQL.

**Solutions:**

1. **Check database is running:**
   ```bash
   docker-compose ps db
   ```

2. **Check database logs:**
   ```bash
   docker-compose logs db
   ```

3. **Wait for database to be ready:**
   ```bash
   # Database has healthcheck, wait for it
   docker-compose up -d db
   sleep 10
   docker-compose up -d backend
   ```

4. **Initialize database:**
   ```bash
   docker-compose exec backend python init_db.py
   ```

### Backend 500 errors

**Solutions:**

1. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Check database connection:**
   ```bash
   docker-compose exec backend python -c "from app.database import engine; engine.connect()"
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

## Gradio Interface Issues

### Gradio not accessible

**Solutions:**

1. **Check if Gradio is running:**
   ```bash
   docker-compose ps gradio
   ```

2. **Check Gradio logs:**
   ```bash
   docker-compose logs gradio
   ```

3. **Verify port 7860 is not in use:**
   ```bash
   # Windows
   netstat -ano | findstr :7860
   
   # Linux/Mac
   lsof -i :7860
   ```

4. **Restart Gradio:**
   ```bash
   docker-compose restart gradio
   ```

## Network Issues

### Containers can't communicate

**Problem:** Services can't reach each other (e.g., frontend can't reach backend).

**Solutions:**

1. **Check Docker network:**
   ```bash
   docker network ls
   docker network inspect <network_name>
   ```

2. **Restart all services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Check service dependencies:**
   Verify `depends_on` in `docker-compose.yml` is correct.

## Port Conflicts

### Port already in use

**Problem:** Port 3000, 8000, or 7860 already in use.

**Solutions:**

1. **Find process using port:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. **Kill process or change port in docker-compose.yml:**
   ```yaml
   ports:
     - "8001:8000"  # Change host port
   ```

3. **Stop conflicting containers:**
   ```bash
   docker ps
   docker stop <container_id>
   ```

## Build Issues

### Build fails with "module not found"

**Solutions:**

1. **Clear Docker build cache:**
   ```bash
   docker-compose build --no-cache
   ```

2. **Check requirements files:**
   - `backend/requirements.txt`
   - `frontend/react-app/package.json`
   - `frontend/gradio-interface/requirements.txt`

3. **Rebuild specific service:**
   ```bash
   docker-compose build --no-cache backend
   docker-compose build --no-cache frontend
   ```

## Quick Fixes

### Full reset (nuclear option)

```bash
# Stop and remove everything
docker-compose down -v

# Remove all containers and images
docker system prune -a

# Rebuild and start
docker-compose up -d --build

# Initialize database
docker-compose exec backend python init_db.py

# Seed data (optional)
docker-compose exec backend python seed_db.py
```

### Check all services health

```bash
# Backend
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:3000

# Gradio
curl http://localhost:7860
```

## Getting Help

1. **Check logs first:**
   ```bash
   docker-compose logs
   ```

2. **Verify configuration:**
   - `docker-compose.yml`
   - `.env` (if using)
   - Service Dockerfiles

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

4. **Test individual services:**
   ```bash
   # Backend
   docker-compose exec backend curl http://localhost:8000/api/health
   
   # Frontend
   docker-compose exec frontend curl http://localhost:80
   ```

## Common Error Messages

### "Cannot connect to Docker daemon"
- Docker Desktop is not running
- Start Docker Desktop

### "Port already allocated"
- Port is in use by another service
- Change port or stop conflicting service

### "No such file or directory"
- Missing files in Docker build context
- Check Dockerfile COPY commands

### "Connection refused"
- Service not running or not ready
- Check logs and wait for healthchecks

