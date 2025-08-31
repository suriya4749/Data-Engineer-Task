from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    "dynamic_scrapy_spider_with_fallback",
    default_args=default_args,
    description="Run a single spider; fallback to all spiders if it fails",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Fetch spider name from Airflow Variables
    spider_name = Variable.get("spider_name", default_var="trucompare")  # default spider

    # Step 1: Ensure environment is ready (optional)
    setup_environment = BashOperator(
        task_id="setup_environment",
        bash_command="cd /opt/airflow/identity-mapping/scraper && scrapy list",
    )

    # Step 2: Run single spider
    run_single_spider = BashOperator(
        task_id="run_single_spider",
        bash_command=f"cd /opt/airflow/identity-mapping/scraper && scrapy crawl {spider_name}",
    )

    # Step 3: Run all spiders if single spider fails
    run_all_spiders = BashOperator(
        task_id="run_all_spiders",
        bash_command="""
        cd /opt/airflow/identity-mapping/scraper && \
        for spider in $(cat /opt/airflow/identity-mapping/spiders.txt); do
            echo "Running spider: $spider"
            scrapy crawl $spider || exit 1
        done
        """,
        trigger_rule=TriggerRule.ONE_FAILED,  # runs if previous task fails
    )

    setup_environment >> run_single_spider >> run_all_spiders
