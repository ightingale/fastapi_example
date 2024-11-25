#!/usr/bin/env bash

set -e

poetry run alembic upgrade head
exec poetry run uvicorn src.entrypoint.web_api:create_app --host 0.0.0.0 --port ${FASTAPI_PORT} --factory
