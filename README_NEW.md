# 🧬 User Management System - FastAPI Edition

A modern, production-ready user management system built with FastAPI, SQLAlchemy, and JWT authentication. This project demonstrates best practices for building scalable web APIs with comprehensive testing, security, and deployment configurations.

## ✨ Features

### 🔥 Core Features
- **🔐 JWT Authentication** - Secure token-based authentication
- **👥 Complete CRUD Operations** - Create, Read, Update, Delete users
- **🔍 Advanced Search** - Case-insensitive search across multiple fields
- **📄 Pagination** - Efficient handling of large datasets
- **🔄 Sorting** - Sort by any field in ascending/descending order
- **📊 Statistics API** - User count and activity metrics
- **✅ Data Validation** - Comprehensive input validation with detailed error messages

### 🛠️ Technical Features
- **⚡ FastAPI** - High-performance async web framework
- **🗃️ SQLAlchemy 2.0** - Modern ORM with async support
- **🗄️ SQLite Database** - Lightweight, reliable database
- **🐳 Docker Support** - Full containerization with multi-stage builds
- **🧪 85%+ Test Coverage** - Comprehensive unit and integration tests
- **🚀 CI/CD Pipeline** - GitHub Actions with automated testing and deployment
- **📈 Load Testing** - Performance testing with Locust
- **🔒 Security** - Input validation, SQL injection prevention, CORS protection
- **📝 Interactive Documentation** - Auto-generated API docs with Swagger UI

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### 🏃‍♂️ Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd user-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Run the application**
   ```bash
   python -m uvicorn user_management.main:app --reload
   ```

5. **Open your browser**
   - **API Documentation**: http://localhost:8000/docs
   - **Frontend**: Open `index_new.html` in your browser
   - **Health Check**: http://localhost:8000/health

### 🐳 Docker Deployment

#### Quick Start with Docker Compose
```bash
# Production deployment
docker-compose up -d

# Development with hot reload
docker-compose --profile dev up -d

# With nginx reverse proxy
docker-compose --profile nginx up -d

# With load testing
docker-compose --profile load-test up -d
```

#### Manual Docker Build
```bash
# Build production image
docker build --target production -t user-management:latest .

# Run container
docker run -d -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="sqlite:///./data/users.db" \
  -v user_data:/app/data \
  user-management:latest
```

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication. Demo credentials are available:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |
| `demo` | `demo123` | Demo User |
| `user` | `user123` | Regular User |

### 🔑 Getting a Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 🛡️ Using the Token
```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📚 API Documentation

### 🔗 Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/login` | Authenticate user | ❌ |
| `GET` | `/api/v1/auth/demo-users` | Get demo credentials | ❌ |
| `GET` | `/api/v1/users/` | List users (with pagination/search) | ❌ |
| `POST` | `/api/v1/users/` | Create new user | ✅ |
| `GET` | `/api/v1/users/{id}` | Get user by ID | ❌ |
| `PUT` | `/api/v1/users/{id}` | Update user | ✅ |
| `DELETE` | `/api/v1/users/{id}` | Delete user | ✅ |
| `GET` | `/api/v1/users/stats/summary` | Get user statistics | ❌ |
| `GET` | `/health` | Health check | ❌ |

### 📖 Detailed Examples

#### Create User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890"
  }'
```

#### Search Users with Pagination
```bash
curl "http://localhost:8000/api/v1/users/?search=john&page=1&limit=10&sort_by=name&sort_order=asc"
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
  }'
```

## 🧪 Testing

### 🔬 Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/user_management --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_user_service.py -v
```

### 📊 Test Coverage
The project maintains 85%+ test coverage with both unit and integration tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete API workflows
- **Authentication Tests**: Verify JWT token handling
- **Database Tests**: Test data persistence and retrieval
- **API Tests**: Test all endpoints with various scenarios

### 🔍 Code Quality
```bash
# Run linting
ruff check src/ tests/

# Format code
black src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/

# Run all quality checks
pre-commit run --all-files
```

## 📈 Performance Testing

### 🚀 Load Testing with Locust
```bash
# Run load test
python scripts/load_test.py --users 100 --spawn-rate 10 --run-time 300s

# Run with custom parameters
python scripts/load_test.py \
  --host http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 180s \
  --output-dir results/
```

### 📊 Performance Metrics
The load testing script provides detailed metrics:
- **Response Times**: Min, max, average, percentiles
- **Throughput**: Requests per second
- **Error Rates**: Success/failure ratios
- **Endpoint Performance**: Per-endpoint statistics
- **Recommendations**: Automated performance suggestions

## 🗄️ Database

### 📋 Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### 🔄 Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current version
alembic current
```

## 🚀 Deployment

### 🐳 Production Deployment with Docker

1. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

### ☁️ Cloud Deployment

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker build -t user-management .
docker tag user-management:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/user-management:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/user-management:latest
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy user-management \
  --image gcr.io/PROJECT_ID/user-management:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 📊 Monitoring

#### Health Checks
- **Basic Health**: `GET /health`
- **Database Health**: Included in health check
- **Metrics**: Response times, error rates

#### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Request Logging**: Automatic request/response logging

## 🔒 Security Considerations

### 🛡️ Implemented Security Measures
- **JWT Authentication**: Secure token-based auth with expiration
- **Input Validation**: Comprehensive Pydantic model validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **CORS Protection**: Configurable cross-origin resource sharing
- **Password Hashing**: bcrypt for secure password storage (demo only)
- **Rate Limiting**: Ready for implementation with Redis
- **Security Headers**: Standard security headers in responses

### 🔐 Production Security Checklist
- [ ] Change default JWT secret key
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable database connection encryption
- [ ] Configure proper firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Database backups
- [ ] Log monitoring

## 🔧 Configuration

### 🌍 Environment Variables
```bash
# Application
APP_NAME="User Management System"
DEBUG=false
VERSION="1.0.0"

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./users.db
DATABASE_ECHO=false

# CORS
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### ⚙️ Configuration Files
- **`pyproject.toml`**: Project metadata and tool configurations
- **`.env`**: Environment-specific settings
- **`alembic.ini`**: Database migration configuration
- **`docker-compose.yml`**: Container orchestration
- **`.pre-commit-config.yaml`**: Code quality hooks

## 🤝 Contributing

### 🔄 Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run quality checks (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### 📝 Code Standards
- **Python**: Follow PEP 8 and use type hints
- **Testing**: Maintain 85%+ test coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages

### 🧪 Setting Up Development Environment
```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests before committing
pytest

# Check code quality
pre-commit run --all-files
```

## 📖 API Schema

The complete API schema is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### Common Issues

#### CORS Errors
```bash
# Update CORS settings in .env
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Database Connection Issues
```bash
# Check database file permissions
ls -la users.db

# Recreate database
rm users.db
alembic upgrade head
```

#### JWT Token Issues
```bash
# Check token expiration
# Tokens expire after 30 minutes by default
# Get a new token from /api/v1/auth/login
```

#### Performance Issues
```bash
# Run performance profiling
python -m cProfile -o profile.prof -m uvicorn user_management.main:app

# Analyze with load testing
python scripts/load_test.py --users 10 --run-time 60s
```

## 📞 Support

- **Documentation**: This README and `/docs` endpoint
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and community support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: For the amazing web framework
- **SQLAlchemy**: For the powerful ORM
- **Pydantic**: For data validation and settings management
- **Pytest**: For the testing framework
- **Docker**: For containerization
- **GitHub Actions**: For CI/CD pipeline

---

**Created with ❤️ by Genetic Invent** 🧬

For more information, visit our [documentation](http://localhost:8000/docs) or check out the [live demo](http://localhost:8000).