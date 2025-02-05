# FastAPI application with SQLAlchemy
This FastAPI application is designed for managing articles and book notes. It supports full CRUD operations and leverages SQLAlchemy, Alembic, PostgreSQL, and Docker for database management and deployment. The project was created for learning purposes.

# Features
- **CRUD Operations**: Create, read, update, and delete projects and their notes.
- **Asynchronous Support**: Fully asynchronous implementation, including async SQLAlchemy for non-blocking database operations.
- **Database Integration**:  Uses SQLAlchemy (async) as the ORM and PostgreSQL as the database backend.
- **Static Typing**: Code is fully typed and checked with MyPy to improve reliability and maintainability
- **Testing**: Includes a comprehensive test suite with pytest, featuring fixtures for setup and teardown.
- **Docker & Docker Compose**: Provides a `docker-compose` setup to easily spin up the FastAPI application along with a PostgreSQL database for development and testing.

# Installation

**Prerequisites**

- Docker & Docker Compose

**Steps:**

**Clone the repository**:\
`git clone https://github.com/AndreiIav/ScholarNotes.git`

**Start the application with Docker Compose**:\
`docker-compose up -d --build`\
This will pull the necessary images, build the FastAPI application, and start both the app and the PostgreSQL database.

**Run the database migrations:**\
`docker-compose exec web alembic upgrade head`

**Access the API documentation**:\
Once the containers are running, open your browser and go to:
- Swagger UI:  http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc

**To bring down the containers and volumes:**\
`docker-compose down -v`

# Testing
Run all the tests:\
`docker-compose exec web pytest`

# Key Python Modules Used
- **FastAPI**: A high-performance web framework for building APIs with Python
- **SQLAlchemy**: A database toolkit and ORM for Python
- **Alembic**: A database migration tool used with SQLAlchemy 
- **pytest**: A testing framework that provides a simple yet powerful way to write and run tests
- **ruff**: A fast Python linter that helps enforce coding standards and detect potential issues
- **mypy**: A static type checker for Python that helps catch type-related errors before runtime



