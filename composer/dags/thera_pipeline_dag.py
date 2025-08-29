from airflow import models
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
import datetime

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

with models.DAG(
    'thera_pipeline_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    trigger_dataflow = BashOperator(
        task_id='trigger_dataflow',
        bash_command='gcloud dataflow jobs run thera-dataflow-job --gcs-location=gs://rachana-interview-poc-dataflow-templates/template-name --region=us-central1',
    )

    load_to_bq = BigQueryInsertJobOperator(
        task_id='load_json_to_bq',
        configuration={
            "load": {
                "sourceUris": ["gs://rachana-interview-poc-thera-staging-events/poc-run/data/*.json"],
                "destinationTable": {
                    "projectId": "rachana-interview-poc",
                    "datasetId": "thera_dataset",
                    "tableId": "session_events",
                },
                "sourceFormat": "NEWLINE_DELIMITED_JSON",
                "writeDisposition": "WRITE_APPEND",
            }
        },
        location="us-central1",
    )

    trigger_dataflow >> load_to_bq
