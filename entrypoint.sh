#!/bin/bash


# Roda migrations
alembic upgrade head

# Inicia a aplicação
poetry run uvicorn --host 0.0.0.0 --port 8000 fastapi_zero.app:app