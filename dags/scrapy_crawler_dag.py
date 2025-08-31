from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    "dynamic_scrapy_spiders",
    default_args=default_args,
    description="Run all Scrapy spiders listed in spiders.txt",
    schedule_interval=None,  # manual trigger only
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Step 1: Ensure environment is ready (optional)
    setup_environment = BashOperator(
        task_id="setup_environment",
        bash_command="cd /opt/airflow/identity-mapping/scraper && scrapy list",
    )

    # Step 2: Run all spiders from spiders.txt
    run_spiders = BashOperator(
        task_id="all_spiders",
        bash_command="""
        cd /opt/airflow/identity-mapping/scraper && \
        for spider in $(cat /opt/airflow/identity-mapping/spiders.txt); do
            echo "Running spider: $spider"
            scrapy crawl $spider || exit 1
        done
        """,
    )

    setup_environment >> run_spiders

