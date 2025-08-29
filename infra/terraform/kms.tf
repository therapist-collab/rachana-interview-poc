########################################
# KMS (CMEK) – 90 day rotation
########################################

resource "google_kms_key_ring" "ring" {
  name     = var.key_ring
  location = var.region
  project  = var.project_id

  depends_on = [google_project_service.apis["cloudkms.googleapis.com"]]
}

resource "google_kms_crypto_key" "cmek" {
  name            = var.crypto_key
  key_ring        = google_kms_key_ring.ring.id
  rotation_period = "7776000s" # 90 days

  labels     = { env = "poc" }
  depends_on = [google_kms_key_ring.ring]
}
# Allow Pub/Sub service agent to use the CMEK
data "google_project" "current" {}

resource "google_kms_crypto_key_iam_binding" "pubsub_cmek_use" {
  crypto_key_id = google_kms_crypto_key.cmek.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = [
    "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  ]
}

# Allow BigQuery to use CMEK
resource "google_kms_crypto_key_iam_binding" "bigquery_cmek_use" {
  crypto_key_id = google_kms_crypto_key.cmek.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members       = [
    "serviceAccount:bq-${data.google_project.current.number}@bigquery-encryption.iam.gserviceaccount.com"
  ]
}

# Allow GCS to use CMEK
resource "google_kms_crypto_key_iam_binding" "gcs_cmek_use" {
  crypto_key_id = google_kms_crypto_key.cmek.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = [
    "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com",
    "serviceAccount:dataflow-poc@${var.project_id}.iam.gserviceaccount.com"
  ]
}

