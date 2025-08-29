from google.cloud import bigquery

def load_json_to_bq(uri, table_id):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    
    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )
    
    load_job.result()
    print(f"Loaded data from {uri} to {table_id}")

if __name__ == "__main__":
    GCS_URI = "gs://rachana-interview-poc-thera-staging-events/poc-run/data*.json"
    TABLE_ID = "rachana-interview-poc.thera_poc.session_events"
    load_json_to_bq(GCS_URI, TABLE_ID)
