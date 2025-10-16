# Sports Game Tracker

🏈 🏀 ⚾ 🏒 A professional-grade sports data aggregation platform that pulls live scores, statistics, and game information across major sports leagues (NFL, NBA, MLB, NHL, College Football).

## 🚀 Project Status

**Development Timeline**: 2 weeks  
**Current Phase**: ✅ MVP Complete - Ready for Deployment  
**Tech Stack**: Django 5.0 + SQLite + Redis + Celery + HTMX  
**Test Coverage**: 92% (100/100 tests passing)  
**Cost**: 100% FREE (no paid services)

### ✅ Completed (Tasks 1-9)
- [x] Django infrastructure setup
- [x] Core models with comprehensive tests (18 tests)
- [x] ESPN API client (26 tests, 95% coverage)
- [x] Data sync service (16 tests, 92% coverage)
- [x] Celery background tasks (15 tests, 98% coverage)
- [x] REST API with DRF (25 tests, 100% passing)
- [x] Manual API testing with sample data
- [x] API documentation (Swagger UI, ReDoc, OpenAPI)
- [x] Frontend dashboard (Django Templates + HTMX)

### 🔄 In Progress (Task 10)
- [ ] Deployment preparation
- [ ] Production settings configuration
- [ ] Environment variables setup
- [ ] Static files collection
- [ ] Deployment documentation

---

## 📋 Features

### Core Features
- ✅ **Live Scores**: Real-time game scores with auto-refresh (HTMX polling)
- ✅ **Multiple Sports**: NFL, NBA, MLB, NHL, College Football, and more
- ✅ **REST API**: Full CRUD operations with filtering, search, and pagination
- ✅ **Web Dashboard**: Modern responsive UI with Django Templates + HTMX + Tailwind CSS
- ✅ **Background Updates**: Automated data refresh using Celery + Redis
- ✅ **Admin Panel**: Django admin for data management
- ✅ **API Documentation**: Interactive Swagger UI and ReDoc with OpenAPI 3.0 schema
- ✅ **Team Pages**: Detailed team information, roster, recent & upcoming games
- ✅ **Game Details**: Period-by-period scores, team stats, live status
- ✅ **Schedule Views**: Browse games by date with league filtering
- ✅ **Standings Tables**: League standings with win-loss records

### Technical Highlights
- 🧪 **Test-Driven Development** (TDD) with pytest
- 📊 **75-80% Test Coverage** (pytest-cov)
- ✨ **Code Quality**: Pylint 8.0+ score
- 🐳 **Docker Ready**: Full Docker Compose setup
- 🔄 **CI/CD**: GitHub Actions integration
- 📝 **Well Documented**: Comprehensive documentation

---

## 🛠️ Technology Stack

### Backend
- **Django 5.x** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Background task processing

### Testing & Quality
- **pytest** - Testing framework
- **pytest-django** - Django integration for tests
- **pytest-cov** - Code coverage reporting
- **factory_boy** - Test fixtures and factories
- **pylint** - Static code analysis
- **black** - Code formatting
- **isort** - Import sorting
- **bandit** - Security linting

### Frontend
- **Django Templates** - Server-side rendering
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **HTMX** - Dynamic updates (optional)
- **Font Awesome** - Icons

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline

### Data Sources (FREE APIs)
- **ESPN Hidden API** - Game data
- **TheSportsDB** - Team/player information
- **API-Sports (RapidAPI)** - Additional sports data

---

## 📁 Project Structure

```
Sports_Game_Tracker/
├── config/                    # Django settings and configuration
│   ├── settings/
│   │   ├── base.py           # Common settings
│   │   ├── development.py    # Dev environment
│   │   └── test.py           # Test environment
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI configuration
├── apps/
│   ├── core/                 # Core models (League, Team, Game, etc.)
│   ├── api/                  # REST API endpoints
│   ├── data_ingestion/       # External API clients and Celery tasks
│   └── web/                  # Frontend views and templates
├── static/                   # Static files (CSS, JS, images)
├── templates/                # HTML templates
├── tests/                    # Integration tests
├── requirements/             # Python dependencies
│   ├── base.txt
│   ├── development.txt
│   └── test.txt
├── docker-compose.yml        # Docker services configuration
├── Dockerfile                # Docker image definition
├── pytest.ini                # Pytest configuration
├── .pylintrc                 # Pylint configuration
├── .gitignore                # Git ignore patterns
├── manage.py                 # Django management script
├── README.md                 # This file
└── OUTLINE.md                # Detailed project plan
```

---

## 🚦 Getting Started

### Prerequisites
- **Python 3.11+** (FREE)
- **Docker & Docker Compose** (FREE)
- **Git** (FREE)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/tatejones2/Sports_Game_Tracker.git
cd Sports_Game_Tracker
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements/development.txt
```

4. **Start Docker services** (PostgreSQL + Redis)
```bash
docker-compose up -d
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Fetch real ESPN data** (NEW - replaces mock data)
```bash
python manage.py sync_games
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Start development server**
```bash
python manage.py runserver
```

9. **Start Celery worker** (in a new terminal)
```bash
celery -A config worker -l info
```

10. **Start Celery beat** (in another terminal)
```bash
celery -A config beat -l info
```

### Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test file
pytest apps/core/tests/test_models.py

# Run tests matching pattern
pytest -k "test_game"

# Verbose output
pytest -v
```

### Code Quality Checks

```bash
# Lint code
pylint apps/

# Format code
black .

# Sort imports
isort .

# Security scan
bandit -r apps/
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://sportsuser:sportspass@localhost:5432/sports_tracker

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (if using paid tiers)
ESPN_API_KEY=optional
SPORTSDB_API_KEY=optional
RAPID_API_KEY=optional
```

---

## 📊 API Endpoints

### Games
- `GET /api/games/` - List all games
- `GET /api/games/{id}/` - Game details
- `GET /api/games/live/` - Currently live games
- `GET /api/games/today/` - Today's games

### Teams
- `GET /api/teams/` - List all teams
- `GET /api/teams/{id}/` - Team details
- `GET /api/teams/{id}/schedule/` - Team schedule

### Leagues
- `GET /api/leagues/` - List all leagues
- `GET /api/leagues/{id}/` - League details

### Players
- `GET /api/players/` - List all players
- `GET /api/players/{id}/` - Player details

For full API documentation, visit `/api/docs/` when the server is running.

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build

# Access database
docker-compose exec db psql -U sportsuser -d sports_tracker
```

---

## 📚 Documentation

- **[OUTLINE.md](OUTLINE.md)** - Detailed 2-week development plan
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference (coming soon)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (coming soon)
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines (coming soon)

---

## 🗓️ Development Timeline

### Week 1: Foundation & Backend
- **Days 1-2**: Project setup & TDD infrastructure
- **Days 3-4**: Data models & API integration
- **Days 5-6**: Data ingestion & Celery tasks
- **Day 7**: REST API development

### Week 2: Frontend & Polish
- **Days 8-9**: Web interface development
- **Day 10**: Testing & quality assurance
- **Day 11**: Documentation & polish
- **Days 12-13**: Additional features & final testing

---

## 🧑‍💻 Development Workflow

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Write tests first** (TDD approach)
3. **Implement feature**
4. **Run tests**: `pytest`
5. **Check coverage**: `pytest --cov`
6. **Lint code**: `pylint apps/`
7. **Format code**: `black .`
8. **Commit changes**: `git commit -m "feat: add your feature"`
9. **Push branch**: `git push origin feature/your-feature`
10. **Create Pull Request**

---

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists
- **Django REST Framework** - Powerful toolkit for building Web APIs
- **ESPN** - Sports data source
- **TheSportsDB** - Free sports database API
- **Bootstrap** - Frontend framework
- All the amazing open-source contributors!

---

## 📧 Contact

**Project Maintainer**: Tate Jones  
**GitHub**: [@tatejones2](https://github.com/tatejones2)  
**Project Link**: [https://github.com/tatejones2/Sports_Game_Tracker](https://github.com/tatejones2/Sports_Game_Tracker)

---

## ⚠️ Legal Disclaimer

This project uses various sports APIs for data. Please ensure you comply with the Terms of Service of each API provider:
- ESPN Hidden API is unofficial and may change without notice
- TheSportsDB requires attribution
- Always check API usage limits and terms

This project is for educational and demonstration purposes. For commercial use, consider obtaining official data licenses from sports leagues.

---

## 🎯 Project Goals

- ✅ Build a professional-grade application in 2 weeks
- ✅ Practice Test-Driven Development (TDD)
- ✅ Demonstrate Django and REST API expertise
- ✅ Create a portfolio-worthy project
- ✅ Keep costs at $0 (100% free)
- ✅ Write clean, maintainable code
- ✅ Achieve 75-80% test coverage

---

**Last Updated**: October 15, 2025  
**Version**: 0.1.0 (Initial Setup)  
**Status**: 🚧 In Development

---

Made with ❤️ and ☕ by Tate Jones
