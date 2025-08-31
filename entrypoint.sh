#!/bin/bash
set -e

# Load optional env vars (from .env)
if [ -f "/opt/airflow/.env" ]; then
  set -o allexport
  source /opt/airflow/.env
  set +o allexport
fi

init_airflow() {
  if [ ! -f "/opt/airflow/airflow_db_initialized" ]; then
    echo "Initializing Airflow DB..."
    airflow db init

    echo "Creating default user (if not exists)..."
    airflow users create \
      --username "${AIRFLOW_USER:-admin}" \
      --firstname "${AIRFLOW_FIRSTNAME:-Admin}" \
      --lastname "${AIRFLOW_LASTNAME:-User}" \
      --role Admin \
      --email "${AIRFLOW_EMAIL:-admin@example.com}" \
      --password "${AIRFLOW_PASSWORD:-admin}" || true

    touch /opt/airflow/airflow_db_initialized
  else
    echo "Airflow DB already initialized, skipping..."
  fi
}

case "$1" in
  webserver)
    init_airflow
    exec airflow webserver
    ;;
  scheduler)
    init_airflow
    exec airflow scheduler
    ;;
  spider)
    shift
    if [ -z "$1" ]; then
      echo "Usage: docker compose run --rm airflow-webserver spider <SPIDER_NAME> [extra scrapy args]"
      exit 1
    fi
    exec scrapy crawl "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
