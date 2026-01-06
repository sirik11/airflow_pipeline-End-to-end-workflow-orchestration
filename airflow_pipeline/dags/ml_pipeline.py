"""
A simple Airflow DAG demonstrating an end‑to‑end ML pipeline.  It includes tasks for ingestion,
preprocessing, model inference, evaluation and reporting, along with a sensor that waits for
input data.  Concurrency parameters and retries are configured to illustrate best practices.

This DAG is designed to run with the KubernetesExecutor; tasks can be converted to
KubernetesPodOperators by replacing PythonOperators accordingly.  For long‑running
sensors, use reschedule mode to free worker slots【762547869258626†L252-L261】.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
# If using the KubernetesExecutor, import KubernetesPodOperator
# from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator


def ingest_data(**context):
    """Placeholder function to simulate data ingestion."""
    print("Ingesting data...")
    # e.g. download files from S3/GCS
    return "data_path"


def preprocess_data(**context):
    """Placeholder function for preprocessing."""
    data_path = context['ti'].xcom_pull(task_ids='ingest_data')
    print(f"Preprocessing data from {data_path}...")
    return "preprocessed_path"


def run_inference(**context):
    """Placeholder function to call the inference engine."""
    preprocessed_path = context['ti'].xcom_pull(task_ids='preprocess_data')
    print(f"Running model on {preprocessed_path}...")
    # In a real pipeline, you might call the C++ inference engine via subprocess or
    # run a KubernetesPodOperator with the inference container.
    return "predictions_path"


def evaluate_results(**context):
    predictions_path = context['ti'].xcom_pull(task_ids='run_inference')
    print(f"Evaluating predictions from {predictions_path}...")
    # compute metrics (accuracy, F1 etc.)
    return "report_path"


def generate_report(**context):
    report_path = context['ti'].xcom_pull(task_ids='evaluate_results')
    print(f"Generating report at {report_path}...")


def _fail_callback(context):
    task_instance = context.get('task_instance')
    print(f"Task {task_instance.task_id} failed. Handling retry...")


def _success_callback(context):
    task_instance = context.get('task_instance')
    print(f"Task {task_instance.task_id} succeeded.")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': _fail_callback,
    'on_success_callback': _success_callback,
}

with DAG(
    dag_id='ml_pipeline',
    description='End-to-end ML pipeline with ingestion, preprocessing, inference, evaluation and reporting',
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    concurrency=4,  # limit concurrent tasks across all runs【222326076921222†L318-L327】
) as dag:
    # Sensor waiting for a file to arrive; use reschedule mode for long waits【762547869258626†L252-L261】
    wait_for_data = FileSensor(
        task_id='wait_for_data',
        filepath='/opt/data/input_ready.flag',
        poke_interval=60,  # check every minute
        timeout=60 * 60,   # time out after one hour
        mode='reschedule',
    )

    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data,
    )

    preprocess_task = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data,
    )

    inference_task = PythonOperator(
        task_id='run_inference',
        python_callable=run_inference,
    )

    evaluate_task = PythonOperator(
        task_id='evaluate_results',
        python_callable=evaluate_results,
    )

    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
        retries=0,  # override default retries for this task【36098019983571†L425-L434】
    )

    # Define dependencies
    wait_for_data >> ingest_task >> preprocess_task >> inference_task >> evaluate_task >> report_task
