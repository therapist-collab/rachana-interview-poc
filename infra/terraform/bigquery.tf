########################################
# BigQuery Dataset + Tables (CMEK)
# NOTE: Exactly one dataset block, then four tables.
########################################

resource "google_bigquery_dataset" "ds" {
  dataset_id = var.dataset_id
  location   = var.location

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.cmek.id
  }

  labels     = { env = "poc" }
  depends_on = [
    google_project_service.apis["bigquery.googleapis.com"],
    google_kms_crypto_key.cmek
  ]
}

resource "google_bigquery_table" "session_events" {
  dataset_id = google_bigquery_dataset.ds.dataset_id
  table_id   = "session_events"
  schema = jsonencode([
    { name = "session_id", type = "STRING", mode = "REQUIRED" },
    { name = "therapist_id", type = "STRING", mode = "REQUIRED" },
    { name = "patient_id", type = "STRING", mode = "REQUIRED" },
    { name = "ts", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "text", type = "STRING", mode = "NULLABLE" },
    { name = "audio_uri", type = "STRING", mode = "NULLABLE" },
    { name = "source", type = "STRING", mode = "NULLABLE" },
    { name = "ingest_id", type = "STRING", mode = "NULLABLE" }
  ])
  labels              = { env = "poc" }
  deletion_protection = false
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_bigquery_table" "message_analytics" {
  dataset_id = google_bigquery_dataset.ds.dataset_id
  table_id   = "message_analytics"
  schema = jsonencode([
    { name = "week_start", type = "DATE", mode = "REQUIRED" },
    { name = "session_id", type = "STRING", mode = "REQUIRED" },
    { name = "theme", type = "STRING", mode = "REQUIRED" },
    { name = "sentiment", type = "STRING", mode = "REQUIRED" },
    { name = "message_count", type = "INTEGER", mode = "REQUIRED" }
  ])
  labels              = { env = "poc" }
  deletion_protection = false
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_bigquery_table" "session_summaries" {
  dataset_id = google_bigquery_dataset.ds.dataset_id
  table_id   = "session_summaries"
  schema = jsonencode([
    { name = "session_id", type = "STRING", mode = "REQUIRED" },
    { name = "summary", type = "STRING", mode = "REQUIRED" },
    { name = "model", type = "STRING", mode = "NULLABLE" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
  labels              = { env = "poc" }
  deletion_protection = false
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_bigquery_table" "therapist_licenses" {
  dataset_id = google_bigquery_dataset.ds.dataset_id
  table_id   = "therapist_licenses"
  schema = jsonencode([
    { name = "therapist_id", type = "STRING", mode = "REQUIRED" },
    { name = "license_id", type = "STRING", mode = "REQUIRED" },
    { name = "status", type = "STRING", mode = "REQUIRED" },
    { name = "status_detail", type = "STRING", mode = "NULLABLE" },
    { name = "last_checked", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
  labels              = { env = "poc" }
  deletion_protection = false
  lifecycle {
    prevent_destroy = false
  }
}
