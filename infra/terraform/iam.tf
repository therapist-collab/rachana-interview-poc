########################################
# Least-privilege Service Accounts (placeholders)
########################################

# Dataflow service account (example)
resource "google_service_account" "dataflow_sa" {
  account_id   = "dataflow-poc"
  display_name = "Dataflow POC SA"
}

# Minimal roles: read from Pub/Sub, write to GCS & BQ
resource "google_project_iam_member" "dataflow_pubsub_sub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "dataflow_pubsub_view" {
  project = var.project_id
  role    = "roles/pubsub.viewer"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "dataflow_gcs_writer" {
  project = var.project_id
  role    = "roles/storage.objectCreator"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "dataflow_bq_writer" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}
