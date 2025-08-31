FROM apache/airflow:2.9.1-python3.12

SHELL ["/bin/bash", "-c"]

# Set workdir
WORKDIR /opt/airflow

# Copy requirements first for caching
COPY --chown=airflow:airflow requirements.txt /opt/airflow/requirements.txt

# Install dependencies as airflow user
USER airflow
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Copy project files
USER root
COPY --chown=airflow:airflow dags/ /opt/airflow/dags/
COPY --chown=airflow:airflow spiders/ /opt/airflow/spiders/
COPY --chown=airflow:airflow pipelines/ /opt/airflow/pipelines/
COPY --chown=airflow:airflow loaders/ /opt/airflow/loaders/
COPY --chown=airflow:airflow .env /opt/airflow/.env

# Optional: custom entrypoint
COPY --chown=airflow:airflow entrypoint.sh /opt/airflow/entrypoint.sh
RUN chmod +x /opt/airflow/entrypoint.sh

USER airflow
WORKDIR /opt/airflow

ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
