########################################
# Pub/Sub (Schema + Topic, CMEK)
# Free-tier: single topic, 7d retention
# HIPAA: CMEK via KMS; Data Access logs enabled at project level (see audit.tf)
########################################

# Avro schema for patient messages
resource "google_pubsub_schema" "patient" {
  name    = var.pubsub_schema
  type    = "AVRO"
  project = var.project_id

  definition = <<-AVSC
  {
    "type":"record",
    "name":"PatientMessage",
    "namespace":"therapist.poc",
    "fields":[
      {"name":"session_id","type":"string"},
      {"name":"therapist_id","type":"string"},
      {"name":"patient_id","type":"string"},
      {"name":"ts","type":{"type":"long","logicalType":"timestamp-millis"}},
      {"name":"text","type":["null","string"],"default":null},
      {"name":"audio_uri","type":["null","string"],"default":null},
      {"name":"source","type":["null","string"],"default":"patient-app"},
      {"name":"ingest_id","type":["null","string"],"default":null}
    ]
  }
  AVSC

  # Ensure Pub/Sub API exists before creating schema
  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}

# Topic with schema and CMEK
resource "google_pubsub_topic" "patient" {
  name    = var.pubsub_topic
  project = var.project_id

  # Attach schema (encode messages as JSON against Avro schema)
  schema_settings {
    schema   = google_pubsub_schema.patient.id
    encoding = "JSON"
  }

  # HIPAA: CMEK for message storage
  kms_key_name = google_kms_crypto_key.cmek.id

  # Keep data regionally pinned and within free tier limits
  message_retention_duration = "604800s" # 7 days
  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }

  labels = { env = "poc" }

  # Ensure API + CMEK are ready (prevents race conditions)
  depends_on = [
    google_project_service.apis["pubsub.googleapis.com"],
    google_kms_crypto_key.cmek
  ]
}
