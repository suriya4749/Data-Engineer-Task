#!/bin/bash

echo "🔴 Stopping Airflow processes..."
pkill -f "airflow webserver"
pkill -f "airflow scheduler"

echo "🗑️ Resetting Airflow DB..."
airflow db reset -y

# Create admin user again
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

echo "🚀 Starting Airflow services..."
airflow webserver -D
airflow scheduler -D

echo "✅ Airflow reset and restarted!"
echo "👉 Open http://localhost:8080 to trigger DAGs manually."
