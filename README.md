# Studget

## Project Description

**Studget** is a modern, AI-powered personal finance management platform designed for students. It enables users to securely track, analyze, and gain insights into their spending habits. By leveraging advanced natural language understanding (NLU) and large language models (LLMs), Studget allows users to interact with their financial data conversationally, generate detailed reports, and receive actionable insights, all while ensuring data privacy and security.

## Features

- **User Authentication:** Secure signup and login with JWT-based authentication.
- **Transaction Management:** Add, retrieve, and categorize expenses with ease.
- **Monthly Reports:** Automated, cached monthly spending summaries and category-wise breakdowns.
- **Spending Controls:** Set and monitor monthly spending limits with visual indicators (Green/Orange/Red).
- **Category Tracking:** Track spending across different categories (Food, Shopping, Transportation, etc.).
- **Trend Analysis:** Monitor spending trends with indicators (New, Increased, Decreased, Stable, Stopped).
- **Conversational Chatbot:** AI-powered chatbot for querying and analyzing expenses using natural language.
- **Intelligent Query Parsing:** Advanced NLU to extract structured data from user queries.
- **Insightful Analytics:** Summarized spending patterns and actionable financial insights.
- **Async & Scalable:** Built with FastAPI and async SQLAlchemy for high performance.
- **Redis Caching:** Fast access to frequently requested reports.

## Tech Stack / Dependencies

- **Backend Framework:** FastAPI
- **ORM:** SQLModel (async with SQLAlchemy)
- **Database:** PostgreSQL (asyncpg, psycopg)
- **Authentication:** JWT (PyJWT, passlib, bcrypt)
- **AI/LLM:** LangChain, Google Gemini (langchain-google-genai)
- **Caching:** Redis (redis[hiredis])
- **Other:** Uvicorn, Pydantic, dateparser, python-multipart

See [pyproject.toml](pyproject.toml) for the full list of dependencies.

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Redis server
- Google Gemini API key

### Installation

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Studget
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   Or, if using [uv](https://github.com/astral-sh/uv):
   ```sh
   uv sync
   ```

3. **Set up environment variables:**
   Create a [`.env`](.env ) file in the root directory with the following variables:
   ```
   db_url=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
   secret_key=your_secret_key
   algorithm=HS256
   redis_host=localhost
   redis_username=your_redis_user
   redis_password=your_redis_password
   redis_port=6379
   google_api_key=your_google_gemini_api_key
   ```

4. **Run database migrations:**
   The database tables are auto-created on startup.

5. **Start the application:**
   ```sh
   uvicorn main:app --reload
   ```

### Running on Render

The project includes a [`render.yml`](render.yml ) for deployment on [Render](https://render.com/).

## API Endpoints / Functionality Overview

All endpoints return a standardized `APIResponse` format with consistent error handling.

### Authentication API
- `POST /auth/login` — User authentication with JWT token response
- `POST /auth/signup` — New user registration

### Profile API
- `GET /profile/student_profile` — Retrieve user profile information
- `GET /profile/monthly_report` — Get detailed monthly spending analysis

### Home Dashboard API
- Transaction Management:
  - `POST /home/add_transaction` — Record a new expense transaction
  - `POST /home/get_transactions` — Fetch transactions with date-based filtering

- Spending Controls:
  - `POST /home/set_monthly_limit/{monthly_limit}` — Configure monthly spending threshold
  - `GET /home/get_monthly_limit` — Retrieve current monthly spending limit
  - `GET /home/get_spending_indicator` — Get spending status (Green/Orange/Red)

### AI and Analytics API
- Chatbot Interface:
  - `POST /bot/studgetbot` — Natural language interface for expense queries
- Automated Analysis:
  - `GET /agent/prev_month_summary` — AI-generated previous month spending summary

## Folder Structure

```
.
├── Auth/                # Authentication routes and logic
├── Dashboard/           # Main dashboard features (profile, home, chatbot, agent)
│   └── Agent/           # AI agent, prompts, and templates for NLU/LLM
├── Database/            # Database models, initialization, and Redis integration
│   ├── Models/          # Pydantic/SQLModel schemas for all entities
│   └── Redis/           # Redis async client setup
├── Utils/               # Utility modules (JWT, password, middleware, exceptions, etc.)
├── main.py              # FastAPI application entry point
├── config.py            # Pydantic settings and environment variable management
├── pyproject.toml       # Project metadata and dependencies
├── render.yml           # Render deployment configuration
└── README.md            # Project documentation
```

- **Auth/**: Handles user authentication (login/signup).
- **Dashboard/**: Contains routes for profile, home dashboard, chatbot, and the AI agent logic.
- **Database/**: All database-related code, including models and Redis setup.
- **Utils/**: Helper utilities for authentication, error handling, dependency injection, and more.
- **[`main.py`](main.py )**: Application startup, middleware, and router registration.
- **[`config.py`](config.py )**: Centralized configuration using environment variables.

## Architecture

The initial architecture and dashboard structure for Studget were planned visually to clarify the project’s flow and modular design. Below are the diagrams that guided the early development:

### Agent Flow

![Agent Flow](Images/Agent%20Flow.png)

This diagram outlines the flow of the AI agent, detailing how user queries are processed and insights are generated.

### Dashboard Structure

![Studget Structure of Dashboard](Images/Studget%20Structure%20of%20Dashboard.png)

This diagram illustrates the modular structure of the dashboard, showing the separation of concerns between authentication, transaction management, analytics, and AI-powered features.

## Screenshots / Demos

Currently Not available.
