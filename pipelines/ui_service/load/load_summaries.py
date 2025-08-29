import argparse
from google.cloud import bigquery

def load_jsonl_to_bq(project, dataset, table, gcs_uri, location="US"):
    client = bigquery.Client(project=project)

    table_id = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",  # Overwrites if table exists
    )

    load_job = client.load_table_from_uri(
        gcs_uri,
        table_id,
        location=location,
        job_config=job_config,
    )

    load_job.result()  # Waits for the job to complete
    print(f"Loaded data into BigQuery table: {table_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dataset", default="thera_poc")
    parser.add_argument("--table", default="session_summaries")
    parser.add_argument("--gcs_uri", required=True)  # gs://.../predictions/predictions-00000-of-00001.jsonl
    args = parser.parse_args()

    load_jsonl_to_bq(
        project=args.project,
        dataset=args.dataset,
        table=args.table,
        gcs_uri=args.gcs_uri
    )
