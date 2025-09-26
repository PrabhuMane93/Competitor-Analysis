from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def run_scraper():
    from scrap_and_dump import scrape
    import configparser

    config = configparser.ConfigParser()
    config.read("companies.config")
    companies = config["companies"]

    for company, url in companies.items():
        print(f"Scraping {company} → {url}")
        scrape(url, company)


local_tz = pendulum.timezone("Europe/Berlin")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="scrape_companies_dag",
    default_args=default_args,
    description="Scrape companies every alternate day at 6 AM German time",
    schedule="0 6 */2 * *",  # every 2 days at 6 AM
    start_date=datetime(2025, 1, 1, tzinfo=local_tz),
    catchup=False,
    tags=["scraping", "companies"],
) as dag:

    scrape_task = PythonOperator(
        task_id="run_scraper_task",
        python_callable=run_scraper,
    )
    scrape_task