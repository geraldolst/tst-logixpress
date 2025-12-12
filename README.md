# LOGIXPress API

[![CI Pipeline](https://github.com/geraldolst/tst-logixpress/actions/workflows/ci.yml/badge.svg)](https://github.com/geraldolst/tst-logixpress/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Code Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](htmlcov/index.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready FastAPI microservice for last-mile delivery shipment lifecycle management.

##  Cara Menjalankan Aplikasi

### Opsi 1: Docker (Recommended)
```bash
# Build dan jalankan container
docker compose up --build

# Atau jalankan di background
docker compose up -d
```

**Akses Aplikasi:**
-  API: http://localhost:8000
-  Dokumentasi Scalar: http://localhost:8000/scalar
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Stop container:**
```bash
docker compose down
```

---

### Opsi 2: Virtual Environment (Local Development)

**Setup (Pertama kali):**
```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan venv (PowerShell)
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

**Jalankan Aplikasi:**
```bash
# Aktifkan venv
.\venv\Scripts\Activate.ps1

# Jalankan dengan FastAPI dev (auto-reload)
fastapi dev

# Atau dengan uvicorn
uvicorn app.main:app --reload --port 8000
```

**Akses Aplikasi:**
- Server berjalan di http://127.0.0.1:8000
- Tekan **Ctrl + Klik** pada URL di terminal
- Dokumentasi Scalar: http://127.0.0.1:8000/scalar

## Project Structure
```
tst-logixpress/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── router.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── shipment.py
│   │   │   ├── tracking.py
│   │   │   └── stats.py
│   │   └── schemas/
│   │       ├── auth.py
│   │       └── shipment.py
│   ├── core/
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── models/
│   │   └── shipment.py
│   └── services/
│       ├── auth.py
│       └── shipment.py
├── tests/
├── data/
├── Dockerfile
├── docker-compose.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## API Overview
All endpoints use JSON with JWT Bearer token authentication.

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new user account | No |
| POST | `/auth/login` | Login and get JWT token | No |
| GET | `/auth/me` | Get current user info | Yes |

### Shipments
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/shipments` | List shipments (filterable) | Any authenticated |
| GET | `/shipment/{id}` | Get shipment details | Any authenticated |
| POST | `/shipment` | Create new shipment | admin, customer |
| PATCH | `/shipment/{id}` | Update shipment | admin, courier |
| DELETE | `/shipment/{id}` | Delete shipment | admin |

### Tracking
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/shipment/{id}/tracking` | Get tracking history | Any authenticated |
| POST | `/shipment/{id}/tracking` | Add tracking event | admin, courier |

### Statistics
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/stats` | Get shipment statistics | admin |
| GET | `/health` | Health check | None |

## Shipment Status Workflow
Shipment lifecycle:

**PLACED** → **IN_TRANSIT** → **OUT_FOR_DELIVERY** → **DELIVERED**

Alternative paths:
- Any status → **CANCELLED**
- IN_TRANSIT/OUT_FOR_DELIVERY → **RETURNED**

### Status Transitions
- `placed`: Initial status when shipment is created
- `in_transit`: Package in transit to destination
- `out_for_delivery`: Package out for delivery to recipient
- `delivered`: Successfully delivered (terminal state)
- `returned`: Package returned to sender (terminal state)
- `cancelled`: Shipment cancelled (terminal state)

**Rules:**
- Only forward transitions allowed (except cancel/return)
- Delivered shipments are immutable
- Status changes automatically create tracking events

## Default Users
| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full access (all operations) |
| Courier | `courier` | `courier123` | Update status, add tracking |
| Customer | `customer` | `customer123` | Create shipments, view own data |

## Example Payloads

### Register User
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "customer"
}
```

### Login
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Create Shipment
```json
{
  "package_details": {
    "content": "Electronic Components",
    "weight": 5.5,
    "dimensions": "30x20x15",
    "fragile": true
  },
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+6281234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Tech Store",
    "email": "sales@techstore.com",
    "phone": "+6281234567891"
  },
  "destination_code": 11002
}
```

### Update Shipment Status
```json
{
  "current_status": "in_transit"
}
```

### Add Tracking Event
```json
{
  "location": "Distribution Center Jakarta",
  "description": "Package sorted and ready for dispatch",
  "status": "in_transit"
}
```

### Get Shipments (with filters)
Query Parameters:
- `status`: Filter by status (placed, in_transit, etc.)
- `destination_code`: Filter by destination
- `limit`: Max results (default: 10, max: 100)

Example: `GET /shipments?status=in_transit&limit=20`

## Example Responses

### Single Shipment Response
```json
{
  "id": 12701,
  "package_details": {
    "content": "Electronic Components",
    "weight": 5.5,
    "dimensions": "30x20x15",
    "fragile": true
  },
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+6281234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Tech Store",
    "email": "sales@techstore.com",
    "phone": "+6281234567891"
  },
  "destination_code": 11002,
  "current_status": "placed",
  "tracking_events": [
    {
      "id": 1,
      "location": "Warehouse",
      "description": "Shipment order created and received at warehouse",
      "status": "placed",
      "timestamp": "2024-12-01T09:00:00"
    }
  ],
  "created_at": "2024-12-01T09:00:00",
  "updated_at": "2024-12-01T09:00:00"
}
```

### Shipment List Response
```json
[
  {
    "id": 12701,
    "content": "Electronic Components",
    "weight": 5.5,
    "current_status": "placed",
    "destination_code": 11002,
    "recipient_name": "John Doe",
    "created_at": "2024-12-01T09:00:00"
  },
  {
    "id": 12702,
    "content": "Steel Rods",
    "weight": 14.7,
    "current_status": "in_transit",
    "destination_code": 11003,
    "recipient_name": "Jane Smith",
    "created_at": "2024-12-01T08:00:00"
  }
]
```

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Model Fields

### ShipmentCreate
- `package_details`: PackageDetails object
- `recipient`: Recipient object
- `seller`: Seller object
- `destination_code`: int

### PackageDetails
- `content`: str (required)
- `weight`: float (required, max 25kg)
- `dimensions`: str | None
- `fragile`: bool (default: false)

### Recipient
- `name`: str (required)
- `email`: EmailStr (required)
- `phone`: str (required)
- `address`: str (required)

### Seller
- `name`: str (required)
- `email`: EmailStr (required)
- `phone`: str (required)

### ShipmentRead
- `id`: int (tracking number)
- `package_details`: PackageDetails
- `recipient`: Recipient
- `seller`: Seller
- `destination_code`: int
- `current_status`: ShipmentStatus
- `tracking_events`: list[TrackingEvent]
- `created_at`: datetime
- `updated_at`: datetime

### TrackingEvent
- `id`: int
- `location`: str
- `description`: str
- `status`: ShipmentStatus
- `timestamp`: datetime

## Role Permissions
All write operations require authentication and proper role:

- **Admin**: Full access to all operations
- **Courier**: Can update shipment status and add tracking events
- **Customer**: Can create shipments and view own data
- **All authenticated**: Can view shipments and tracking

## Error Handling
- `400`: Bad request or validation error
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not found
- `422`: Validation error (Pydantic)
- `500`: Internal server error

## Unit Testing

**Test Coverage: 97%** - Comprehensive test suite with 102 test cases following TDD methodology.

### Test Categories
- ✅ **Authentication** (18 tests): Login, registration, token validation, password security
- ✅ **CRUD Operations** (23 tests): Create, read, update, delete shipments
- ✅ **Tracking** (9 tests): Event management, history tracking
- ✅ **Security** (13 tests): JWT validation, RBAC, injection attempts
- ✅ **Service Layer** (15 tests): Business logic, error handling
- ✅ **Domain Models** (5 tests): Status transitions, validation rules
- ✅ **Statistics** (6 tests): Admin stats, health checks
- ✅ **Edge Cases** (13 tests): Boundary conditions, special characters, concurrency

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/[filename].py -v

# Run specific test function
pytest tests/test_auth.py::TestAuthEndpoints::test_login_success -v

# Run with output capture disabled (see print statements)
pytest tests/ -v -s
```

### Coverage Report
After running tests with coverage, view the HTML report:
```bash
# Open htmlcov/index.html in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Configuration
- **Framework**: pytest 7.4.3
- **Coverage Tool**: pytest-cov 4.1.0
- **Async Support**: pytest-asyncio 0.21.1
- **HTTP Client**: httpx 0.25.2
- **Minimum Coverage**: 95% (configured in pytest.ini)
- **Current Coverage**: 97% (483 statements, 15 missed)

## CI/CD Pipeline

### Automated Workflows
The project uses GitHub Actions for continuous integration and deployment:

#### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
Triggered on push/PR to `main` and `develop` branches.

**Jobs:**
-  **Linting**: Code quality checks (Black, Ruff, Flake8) -> Still fail
-  **Testing**: Run 102 unit tests with 97% coverage
-  **Docker Build**: Build and test Docker image
-  **Docker Compose**: Verify multi-container setup
-  **Integration**: End-to-end API tests
-  **Summary**: Overall pipeline status

#### 2. **Linting Workflow** (`.github/workflows/lint.yml`)
Standalone code quality checks:
- Black formatter validation
- Ruff linter (modern Python linter)
- Flake8 style guide enforcement
- MyPy type checking (optional)

### Running Locally

```bash
# Install linting tools
pip install black ruff flake8 mypy

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Style check
flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503

# Type check
mypy app/ --ignore-missing-imports
```

### CI Configuration Files
- `.github/workflows/ci.yml`: Main CI pipeline
- `.github/workflows/lint.yml`: Code quality workflow
- `pyproject.toml`: Tool configurations (Black, Ruff, pytest, coverage)
- `pytest.ini`: Test runner configuration
- `.gitignore`: Exclude build artifacts and cache

### What CI Checks
✅ Code formatting (Black)  
✅ Linting (Ruff, Flake8)  
✅ Type safety (MyPy)  
✅ Unit tests (pytest)  
✅ Code coverage (>95%)  
✅ Docker build  
✅ Docker Compose  
✅ Integration tests  
✅ Health checks  
✅ API endpoints  

All checks must pass before merging to main branch.

## Docker Usage
```bash
# Build and run
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild
docker compose build --no-cache
```

**Endpoints:**
- App: http://localhost:8000
- Docs: http://localhost:8000/docs
- Scalar: http://localhost:8000/scalar
- Health: http://localhost:8000/health

## Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
python run.py
# or
uvicorn app.main:app --reload --port 8000

# Check code (if dev tools installed)
black app/ tests/           # Format
ruff check app/ tests/      # Lint
mypy app/                   # Type check
```

## Architecture
**Domain-Driven Design (DDD)** with modular structure:

- **API Layer** (`app/api/`): FastAPI routers, dependencies, schemas
- **Core Layer** (`app/core/`): Security, exceptions, utilities
- **Domain Layer** (`app/models/`): Domain models and business rules
- **Service Layer** (`app/services/`): Business logic and operations
- **Configuration** (`app/config.py`): Centralized settings

**Benefits:**
- Clean separation of concerns
- Easy to test and maintain
- Scalable architecture
- Following FastAPI best practices

# View API docs
https://https://tst-logixpress.vercel.app/docs
```

---

**Author**: Geraldo Linggom Samuel Tampubolon (18223136)  
**Course**: TST (Teknologi Sistem Terintegrasi) - ITB  
**Repository**: https://github.com/geraldolst/tst-logixpress