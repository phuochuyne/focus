# focus backend

This backend was assembled from your completed feature implementations by
Zorentia Backend Generator.

Follow the setup instructions below. If you encounter an error while setting up
or running the project, copy the error message into Goat Helper for step-by-step help.

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and replace the example values.
5. Connect to the MySQL database prepared in Database Designer and confirm its
   generated tables are present. Apply `database/schema.sql` once only when
   setting up a new empty database.
6. Run tests: `pytest -q`
7. Start the application:
   `flask --app 'backend:create_app()' run --debug`

The generated API health endpoint is `GET /health`.

## Understand this codebase

- `backend/app.py` creates the Flask application and registers the feature routes.
- `backend/features/` contains each feature's handlers and application logic.
- `backend/core/` contains shared database access, authentication, errors and configuration.
- `database/schema.sql` defines the MySQL tables used by those handlers.
- `tests/` contains generated checks. Run them locally; their presence does not mean
  they were executed or that every business scenario is covered.

API requests reach a registered feature handler, which uses the shared database
helpers to read or update MySQL. Configure the connection in `.env` before use.
Do not reapply the schema to a database that already contains the generated tables.
For a full-stack package, use `README-FULLSTACK.md` for the frontend entry point.

## Verification results

Open [VERIFICATION.md](VERIFICATION.md) for stage reports, recorded findings,
file/feature identifiers, debugging evidence and checks that were not run.
Failed earlier attempts are documented separately from checks on packaged files.
