# Airflow ML Pipeline

This directory contains a sample Airflow DAG that orchestrates a multi‑step machine‑learning workflow: data ingestion, preprocessing, model inference, evaluation and reporting.  The pipeline is designed to be run with the **KubernetesExecutor** for scalability, but it can also run on the Local or Celery executors.

## DAG overview

The DAG `ml_pipeline` defines five primary tasks:

1. **wait_for_data** – uses a `FileSensor` to wait until an input marker file exists.  It runs in `reschedule` mode so that the worker slot is freed during long waits【762547869258626†L252-L261】.
2. **ingest_data** – placeholder Python function that would download or read raw data into the processing environment.
3. **preprocess_data** – cleans and transforms the raw data into the format expected by the model.
4. **run_inference** – calls the model inference engine.  In a production setting you might use a `KubernetesPodOperator` to run the inference container inside Kubernetes.
5. **evaluate_results** – computes evaluation metrics (e.g. accuracy) and returns a path to an evaluation report.
6. **generate_report** – generates a final report or publishes metrics.

Tasks use XComs to pass paths between stages.  Default arguments specify retries and retry delay; the reporting task overrides retries to zero to ensure failures bubble up quickly【36098019983571†L425-L434】.  The DAG sets `max_active_runs=1` and `concurrency=4` to limit concurrency【222326076921222†L318-L327】.

## Running the DAG

1. Install Apache Airflow using the provided `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ````

2. Start Airflow with a suitable executor (e.g. `LocalExecutor` for local testing or `KubernetesExecutor` in Kubernetes).

3. Place the DAG file in your `$AIRFLOW_HOME/dags` directory.

4. Create the marker file (e.g. `/opt/data/input_ready.flag`) or modify the `FileSensor` path in the DAG.

5. Trigger the DAG via the Airflow UI or CLI.

### Deploying with KubernetesExecutor

When running with the KubernetesExecutor, each task runs in its own pod.  Adjust the DAG’s concurrency and resource limits to match your cluster capacity.  Set global `parallelism` and `max_active_tasks_per_dag` in your `airflow.cfg`【222326076921222†L204-L229】 and tune `worker_pods_creation_batch_size` to allow the scheduler to launch multiple pods per loop【222326076921222†L412-L427】.

Create a custom Docker image containing your code and dependencies (e.g. `python:3.9` plus `apache-airflow` and libraries).  Configure Airflow’s `kubernetes_executor_container_repository` and `kubernetes_executor_container_tag` to point at your image.

### Sensors and custom operators

Sensors that wait for external conditions should use `mode='reschedule'` and a long `poke_interval` to free the worker slot while waiting【762547869258626†L252-L261】.  Custom operators can be defined in the `plugins` directory; they can encapsulate tasks like downloading data from S3 or running shell commands.  Use `retries` and `retry_delay` in `default_args` to control fault tolerance【36098019983571†L425-L434】.

## Further work

- Implement actual ingestion/preprocessing/inference/evaluation logic.
- Instrument tasks with Prometheus metrics using the `prometheus_client` library.  Track processed records, errors and task durations【337963513427967†L95-L160】.
- Build Grafana dashboards to visualise pipeline latency, throughput and success rates.

