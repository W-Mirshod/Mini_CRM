# Mini-CRM Lead Distribution

A small Python service for distributing leads to operators based on source-specific weights and operator workload limits.

## Tech Stack

- **Language**: Python 3.11
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy (Async)
- **Database**: SQLite (`aiosqlite`)
- **Migrations**: Alembic
- **Containerization**: Docker

## How to Run

### Using Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`.

### Local Development

1. Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Run migrations:
    ```bash
    alembic upgrade head
    ```

3. Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```

## Data Model

- **Operator**: Handles leads. Has a workload limit and active status.
- **Source (Bot)**: Channel where leads come from.
- **Lead**: Represents a customer (unique by identifier).
- **Contact**: An interaction between a Lead and a Source, assigned to an Operator.
- **SourceOperatorConfig**: Defines the weight of an Operator for a specific Source.

## Distribution Algorithm

When a new contact is created (`POST /contacts/`):

1. **Identify Lead**: Finds an existing lead by identifier or creates a new one.
2. **Identify Eligible Operators**: Finds operators linked to the source who are active.
3. **Check Workload**: Filters out operators who have reached their workload limit (current contact count >= limit).
4. **Weighted Selection**: Randomly selects an operator from the eligible list based on their configured weights.
5. **Assignment**: Creates the contact and assigns the selected operator. If no operator is eligible, the contact is created without an assignment.

## API Endpoints

- `POST /operators/`: Create operator
- `GET /operators/`: List operators
- `PATCH /operators/{id}`: Update activity/limit
- `POST /sources/`: Create source
- `POST /sources/{id}/weights`: Set operator weights
- `POST /contacts/`: Register a new contact (triggers distribution)
- `GET /leads/`: List leads
- `GET /stats/`: Show distribution statistics
