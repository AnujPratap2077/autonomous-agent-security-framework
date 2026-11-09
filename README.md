# Behavioral Anomaly Detection Framework for Autonomous AI Agents

**AGENT//SENTINEL** is a lightweight security monitoring framework designed to detect suspicious and abnormal behaviour in autonomous AI agents.

It collects agent activity events, analyzes them using rule-based detection and behavioural baselines, assigns risk scores, stores events persistently, and presents monitoring results through a web dashboard.

## 1. Project Overview

Autonomous AI agents can perform actions such as API requests, database operations, and file access. Unexpected or malicious actions can create security risks.

AGENT//SENTINEL provides a centralized way to:

- Monitor activities performed by autonomous agents.
- Collect and validate agent activity events.
- Detect suspicious behaviour using hybrid anomaly detection.
- Calculate risk scores and classify security risks.
- Store events persistently using SQLite.
- Protect API endpoints using API key authentication.
- Visualize monitoring and security results through a web dashboard.

## 2. System Architecture

```text
       Autonomous AI Agent
                |
                v
        HTTP Client SDK
                |
                v
          FastAPI Backend
                |
                v
           Event Monitor
                |
                v
         SQLite Event Storage
                |
                v
       Hybrid Detection Engine
          /           \
         v             v
   Rule-Based       Behavioural
   Detection         Analysis
          \           /
           v         v
          Risk Assessment
                |
                v
         Security Reports
                |
                v
        AGENT//SENTINEL
          Web Dashboard
```

## 3. Key Features

### Agent Activity Monitoring

- Collects events from autonomous agents.
- Tracks successful, failed, and blocked actions.
- Supports individual and batch event submission.
- Validates incoming event data.

### Hybrid Anomaly Detection

**Rule-based detection**

- Excessive API requests.
- Restricted resource access.
- Repeated failed actions.

**Behavioural detection**

- Builds behavioural baselines from historical agent sessions.
- Extracts activity features.
- Identifies deviations from established behaviour.

### Risk Assessment

- Assigns risk scores from 0 to 100.
- Classifies detected risks into four levels.

| Risk score | Risk level |
| ---------- | ---------- |
| 0–19       | Low        |
| 20–49      | Medium     |
| 50–79      | High       |
| 80–100     | Critical   |

### Persistent Storage

- Uses SQLite to store agent activity events.
- Retains events across backend restarts.
- Requires no external database server.

### API Security

- API key authentication for protected endpoints.
- Request body size limit of 1 MB.
- Batch submission limit of 1,000 events.
- Input validation and field length restrictions.
- API key is kept server-side and is not included in the frontend build.

### Security Dashboard

- Displays event statistics.
- Provides monitoring and anomaly information.
- Shows risk assessment results.
- Communicates with the backend API through the configured Vite proxy.

## 4. Technology Stack

| Component                   | Technology            |
| --------------------------- | --------------------- |
| Programming language        | Python 3.13           |
| Backend                     | FastAPI               |
| API server                  | Uvicorn               |
| Data validation             | Pydantic              |
| HTTP communication          | HTTPX                 |
| Database                    | SQLite                |
| Frontend                    | HTML, CSS, JavaScript |
| Frontend development server | Vite                  |
| Testing                     | Pytest                |
| Version control             | Git and GitHub        |

## 5. Project Structure

```text
autonomous-agent-security-framework/
│
├── configs/
├── data/
├── docs/
├── examples/
│   └── external_agent.py
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── cursor.js
│   │   └── dashboard.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│
├── src/
│   └── agent_security/
│       ├── api/
│       ├── collectors/
│       ├── database.py
│       ├── events.py
│       ├── client.py
│       └── simulator.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 6. Installation and Setup

### Prerequisites

- Python 3.13
- Node.js and npm
- Git

### Step 1: Clone the repository

```bash
git clone https://github.com/AnujPratap2077/autonomous-agent-security-framework.git

cd autonomous-agent-security-framework
```

### Step 2: Create a Python virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Configure the API key

Generate a local API key and save it in the root `.env` file:

```powershell
python -c "from pathlib import Path; import secrets; Path('.env').write_text('AGENT_SENTINEL_API_KEY=' + secrets.token_urlsafe(32) + '\n', encoding='utf-8')"
```

The API key is generated locally. Do not commit the `.env` file or share its contents.

### Step 5: Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

## 7. Running the Project

The backend and frontend run in separate terminals.

### Terminal 1: Start the backend

From the project root, with the virtual environment activated:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn agent_security.api.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Terminal 2: Start the frontend

From the project root:

```powershell
cd frontend
npm run dev
```

Open the local URL displayed by Vite in your browser.

The dashboard communicates with the backend through the configured Vite API proxy.

## 8. External Agent Simulation

The project includes an external agent simulation to demonstrate normal and suspicious agent behaviour.

From the project root, open another PowerShell terminal, activate the virtual environment, and run:

```powershell
$env:PYTHONPATH = "src"
python examples/external_agent.py
```

The simulation demonstrates:

**Normal agent behaviour**

- Sends 3 normal activity events.
- Expected risk score: 0.
- Expected risk level: Low.

**Suspicious agent behaviour**

- Sends 6 suspicious activity events.
- Generates excessive API requests.
- Attempts restricted file access.
- Performs repeated failed actions.
- Expected risk score: 100.
- Expected risk level: Critical.

Each simulation run generates unique session identifiers to prevent previous sessions from affecting its individual analysis.

## 9. API Endpoints

| Method | Endpoint        | Description                       |
| ------ | --------------- | --------------------------------- |
| GET    | `/health`       | Checks backend health             |
| POST   | `/events`       | Submits an individual event       |
| POST   | `/events/batch` | Submits multiple events           |
| GET    | `/events`       | Retrieves stored events           |
| GET    | `/summary`      | Returns event statistics          |
| GET    | `/analyze`      | Analyzes agent behaviour and risk |

### Authentication

The `/health` endpoint is publicly accessible.

The following endpoints require a valid API key:

- `POST /events`
- `POST /events/batch`
- `GET /events`
- `GET /summary`
- `GET /analyze`

Authenticated requests must include the `X-API-Key` HTTP header.

The API key is loaded from the root `.env` file. The Python SDK and development proxy use this configuration to authenticate requests.

Interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

## 10. Running Tests

Run the complete test suite from the project root:

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
```

**Latest verification: 54 tests passed.**

The test suite covers unit and integration functionality.

## 11. Frontend Production Build

To verify that the frontend can be built for production, run:

```powershell
cd frontend
npm run build
```

The generated production files are placed in the `frontend/dist/` directory.

The development API key is injected through the Vite development proxy and is not included in the generated frontend bundle.

## 12. Database

The framework uses SQLite for persistent event storage.

The database is created locally at:

```text
data/agent_events.db
```

The database is generated automatically when the backend initializes. It does not require a separate database installation or account.

Database files are excluded from Git to avoid uploading local runtime data.

## 13. Project Scope and Limitations

This project is an academic security monitoring prototype.

- Detection depends on configured rules and available behavioural history.
- Behavioural baselines require sufficient historical sessions.
- The included external agent is a simulation, not a production autonomous AI platform.
- The framework monitors and assesses suspicious behaviour; it does not independently terminate or contain external agents.
- A `blocked` event represents an action reported as blocked by the agent, not an enforcement action performed by AGENT//SENTINEL.
- Production deployment would require additional operational security, access management, monitoring, and scalability measures.

## 14. Future Improvements

- Integration with additional autonomous agent platforms.
- More advanced behavioural analysis.
- Real-time alert notifications.
- Role-based access control.
- Expanded security testing and evaluation.

## 15. Author and Repository

**GitHub Repository:**

https://github.com/AnujPratap2077/autonomous-agent-security-framework

---

**AGENT//SENTINEL — Monitoring Autonomous Agent Behaviour. Detecting Security Anomalies.**
