# Smart Home Energy Monitoring Platform

![Platform Demo](https://i.imgur.com/8Q9tG2L.png) A full-stack application designed to help users monitor, understand, and query their smart home energy consumption using a modern, responsive interface and a powerful conversational AI.

This project features a complete backend API built with FastAPI, a scalable database schema managed with Alembic, and a dynamic frontend built with React, TypeScript, and `shadcn/ui`. The conversational AI uses a hybrid parsing strategy to answer natural language questions about energy usage.

## Core Features

- **Secure Authentication:** JWT-based login and registration flow.
- **Device Management:** API endpoints to create, list, and manage user-owned smart devices.
- **High-Throughput Telemetry Ingestion:** A robust endpoint designed to handle streams of device energy data.
- **Conversational AI:** A hybrid AI service that can answer natural language questions (e.g., "What was my max usage yesterday?") by using a fast, deterministic parser with a fallback to a powerful LLM (like Claude).
- **Responsive UI:** A modern, type-safe frontend built with React, TypeScript, and styled with Tailwind CSS and `shadcn/ui`.
- **Data Visualization:** Interactive charts displaying energy usage statistics for each device.

## Tech Stack

| Area              | Technology                                                                                                   |
| :---------------- | :----------------------------------------------------------------------------------------------------------- |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Alembic (for migrations), Pydantic, `passlib[bcrypt]`, `python-jose` |
| **Frontend** | React, TypeScript, Vite, `react-router-dom`, Axios, Tailwind CSS, `shadcn/ui`, Recharts                    |
| **Database** | PostgreSQL (compatible with local, Railway, or managed services like Neon)                                 |
| **Dev Environment** | `pipenv` (Python), `nvm` & `npm` (Node.js)                                                            |
| **Deployment** | Docker, Railway.app                                                                                        |

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11+
- `pipenv`
- Node.js v22 (it is recommended to use `nvm` to manage Node versions)
- A running PostgreSQL instance (or credentials for a managed service like Neon or Railway)

## Setup and Installation

Follow these steps to set up the project locally.

### 1. Backend Setup

First, navigate to the backend directory and set up the environment.

```bash
cd smart-home-energy/backend
pipenv install --dev
pipenv run alembic upgrade head
pipenv run uvicorn app.main:app --port 8000 --reload
```
### 2. Frontend Setup
In a separate terminal,
```bash
cd smart-home-energy/frontend
nvm use
npm install
npm run dev
```

### Using the Application
You can use the following credentials for a test user, which can be created via the seed script or the registration UI.

Email: user_1@example.com
Password: password

### Running Tests
To run the backend test suite, navigate to the backend/ directory and run:

```bash
pipenv run pytest
```


