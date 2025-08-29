from datetime import datetime, timedelta
from google.cloud import bigquery
from transformers import pipeline

# BigQuery setup
bq_client = bigquery.Client()

# Constants
BQ_DATASET = "thera_poc"
BQ_SOURCE_TABLE = "session_events"
BQ_DEST_TABLE = "message_analytics"

# HuggingFace pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Query session text
query = f"""
SELECT session_id, text, ts
FROM `{BQ_DATASET}.{BQ_SOURCE_TABLE}`
WHERE text IS NOT NULL
"""

rows = bq_client.query(query).result()

# Prepare records
records = []

for row in rows:
    result = sentiment_pipeline(row.text)[0]
    label = result["label"]  # POSITIVE/NEGATIVE
    week_start = row.ts.date() - timedelta(days=row.ts.weekday())  # Monday of the week

    records.append({
        "week_start": week_start.isoformat(),
        "session_id": row.session_id,
        "theme": "sentiment",        # placeholder — adjust if you have topics
        "sentiment": label,
        "message_count": 1           # could be a count of texts, simplified to 1 per row
    })

# Insert to BigQuery
errors = bq_client.insert_rows_json(
    f"{BQ_DATASET}.{BQ_DEST_TABLE}", records
)

if errors:
    print("Insert errors:", errors)
else:
    print("Sentiment inserted successfully!")
