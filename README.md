# airflow_pipeline-End-to-end-workflow-orchestration

Purpose: This folder contains a sample Apache Airflow DAG that strings together the typical stages of an ML pipeline: waiting for data, ingestion, preprocessing, inference, evaluation and reporting. It illustrates good practices for retries, sensors, concurrency and KubernetesExecutor settings.
Key files and their roles:
dags/ml_pipeline.py – The DAG definition:
Sets default_args with owner, retries, retry delay and callbacks.
Defines a FileSensor in reschedule mode to wait for an input marker file; reschedule frees up the worker slot during long waits
airflow.apache.org
.
Adds PythonOperator tasks: ingest_data, preprocess_data, run_inference, evaluate_results and generate_report. These are placeholders; you can replace them with real logic or KubernetesPodOperator tasks that run the containerised inference engine.
Sets max_active_runs=1 and concurrency=4 at the DAG level to prevent too many concurrent tasks
astronomer.io
. The report task overrides the default retries to zero
airflow.apache.org
.
requirements.txt – Lists Python dependencies (Airflow 2.7.3 and any optional providers you might add).
README.md – Describes:
The purpose of each task and how they pass data via XComs.
Steps to install Airflow, add the DAG to your environment and run it locally.
How to deploy Airflow with the KubernetesExecutor, including tuning parallelism, max_active_tasks_per_dag
astronomer.io
 and worker_pods_creation_batch_size
astronomer.io
 for better performance.
Tips on using sensors in reschedule mode and creating custom operators.
Getting started:
Install Airflow in a virtual environment using:
pip install -r requirements.txt
Copy ml_pipeline.py into your Airflow DAGs directory and start the webserver and scheduler.
Create the marker file the FileSensor watches (or modify the filepath in the DAG).
Trigger the DAG from the UI; each task prints progress. Replace the placeholder functions with your actual ingestion/preprocessing/inference/evaluation code.
For production deployment on Kubernetes, build a Docker image containing Airflow and your DAGs, configure the KubernetesExecutor, and tune concurrency settings as described in the README.
By drilling into these files and their accompanying READMEs, you’ll find all the instructions, code and scripts needed to compile, run, containerise, deploy and orchestrate your machine‑learning inference pipeline.
