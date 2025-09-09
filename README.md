# TutupLapak

A backend API project for Project Sprint's Marketplace Task.

## Project Structure
We use the best practise project structure mentioned in the [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)

```
tutup_lapak/
├── alembic/
├── src/
│   ├── auth/
│   │   ├── router.py
│   │   ├── schemas.py  # pydantic models
│   │   ├── models.py  # db models
│   │   ├── dependencies.py
│   │   ├── config.py  # local configs
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── users/
│   │   └── (same structure)
│   ├── files/
│   │   └── (same structure)
│   ├── config.py  # global configs
│   ├── models.py  # global models
│   ├── exceptions.py  # global exceptions
│   ├── pagination.py  # global module e.g. pagination
│   ├── database.py  # db connection related stuff
│   └── main.py
├── tests/
│   ├── auth/
│   ├── users/
│   └── files/
├── .env
├── .gitignore
├── logging.ini
└── alembic.ini
```

## Setup

### Prerequisites

- External PostgreSQL database server
- Update `.env` file with your database connection details

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

### Docker Setup

1. Update `.env` with your external PostgreSQL database URL
2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at `http://localhost:8000`

### Docker Commands

- Build the image: `docker build -t tutup-lapak .`
- Run the container: `docker run -p 8000:8000 --env-file .env tutup-lapak`

## Features (To be implemented)

- Authentication & Authorization
- User Profile Management
- File Upload

## License

Apache License