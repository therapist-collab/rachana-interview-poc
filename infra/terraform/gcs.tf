########################################
# GCS Buckets (Uniform ACL + CMEK)
########################################

resource "google_storage_bucket" "raw_audio" {
  name                        = "${var.project_id}-${var.raw_bucket}"
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.cmek.id
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition {
      age = 14 # auto-clean demo data to stay well under free tier
    }
  }

  labels     = { env = "poc", purpose = "raw-audio" }
  depends_on = [google_project_service.apis["storage.googleapis.com"]]
}

resource "google_storage_bucket" "staging_events" {
  name                        = "${var.project_id}-${var.staging_bucket}" # <-- use staging_bucket
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.cmek.id
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition {
      age = 14
    }
  }

  labels     = { env = "poc", purpose = "staging-events" }
  depends_on = [google_project_service.apis["storage.googleapis.com"]]
}
