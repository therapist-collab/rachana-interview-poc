variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Default region for resources"
  type        = string
  default     = "us-central1"
}


variable "dataset_id" {
  description = "BigQuery dataset name"
  type        = string
  default     = "thera_poc"
}

variable "raw_bucket" {
  description = "GCS bucket for raw audio"
  type        = string
  default     = "thera-raw-audio"
}

variable "staging_bucket" {
  description = "GCS bucket for staging events"
  type        = string
  default     = "thera-staging-events"
}

variable "pubsub_topic" {
  description = "Pub/Sub topic for session events"
  type        = string
  default     = "thera-session-events"
}

variable "pubsub_schema" {
  description = "Pub/Sub schema name"
  type        = string
  default     = "thera-session-schema"
}

# KMS
variable "key_ring" {
  description = "KMS key ring name"
  type        = string
  default     = "thera-keyring"
}

variable "crypto_key" {
  description = "KMS crypto key name"
  type        = string
  default     = "thera-cmek"
}

variable "kms_location" {
  type    = string
  default = "us-central1"
}





variable "location" {
  description = "Location for multi-region services (e.g., BigQuery, GCS)"
  type        = string
  default     = "us-central1" # was "US"
}

variable "dataset_location" {
  type    = string
  default = "us-central1" # was "US"
}

variable "bucket_location" {
  type    = string
  default = "us-central1" # was "US"
}
