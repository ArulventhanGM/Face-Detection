# Face Recognition System - Deployment Guide

## Production Deployment

### Backend Deployment

#### Using Gunicorn (Linux/Mac)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using Windows IIS
1. Install IIS with CGI support
2. Install wfastcgi: `pip install wfastcgi`
3. Configure IIS to serve the Flask application

#### Using Docker
```dockerfile
# Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Frontend Deployment

#### Build for Production
```bash
cd frontend
npm run build
```

#### Deploy to Static Hosting
- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your Git repository
- **AWS S3**: Upload build files to S3 bucket
- **Apache/Nginx**: Serve the build folder as static files

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/build;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Configuration

#### Backend Environment Variables
```bash
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=sqlite:///production.db
UPLOAD_FOLDER=/var/uploads
MAX_CONTENT_LENGTH=16777216
```

#### Frontend Environment Variables
```bash
# .env.production
REACT_APP_API_URL=https://your-api-domain.com/api
```

### Database Migration

#### For Production Database
```python
# Use PostgreSQL or MySQL for production
# Install: pip install psycopg2-binary  # for PostgreSQL
# Or: pip install mysql-connector-python  # for MySQL

# Update models.py to use production database
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
```

### Security Checklist

- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication and authorization
- [ ] Sanitize file uploads
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Regular security updates
- [ ] Backup database regularly

### Performance Optimization

#### Backend
- Use caching for face encodings
- Implement async processing for large images
- Add database indexing
- Use CDN for image serving

#### Frontend
- Enable gzip compression
- Use image lazy loading
- Implement code splitting
- Add service worker for caching

### Monitoring and Logging

#### Backend Logging
```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

#### Health Checks
- Set up monitoring for `/api/health` endpoint
- Monitor database connectivity
- Track face recognition processing times
- Alert on high error rates

### Backup Strategy

#### Database Backup
```bash
# SQLite backup
cp database.db backups/database_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL backup
pg_dump your_database > backup.sql
```

#### File Backup
```bash
# Backup uploaded images
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### Load Balancing

#### Multiple Backend Instances
```bash
# Start multiple instances
gunicorn -w 4 -b 0.0.0.0:5001 app:app &
gunicorn -w 4 -b 0.0.0.0:5002 app:app &
```

#### Load Balancer Configuration (Nginx)
```nginx
upstream backend {
    server localhost:5001;
    server localhost:5002;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```
