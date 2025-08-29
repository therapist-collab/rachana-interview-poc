# Terraform – Day 2 Baseline

This folder contains a free‑tier, HIPAA‑aware scaffold:
- KMS CMEK (90‑day rotation)
- GCS buckets (uniform access) for `raw-audio` and `staging-events`
- BigQuery dataset + tables
- Pub/Sub Avro schema + topic (JSON encoding)
- Audit logs (DATA_READ/WRITE) for Pub/Sub, GCS, BQ
- Placeholders for VPC‑SC and Private Google Access (doc‑first)

