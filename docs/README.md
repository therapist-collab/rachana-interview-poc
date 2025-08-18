# Therapist Analytics POC — Day 1

## Scope & Success Criteria
The goal is to show a simple end-to-end path:  
Patient message → Pub/Sub → Dataflow → GCS → Composer → BigQuery → Vertex AI → Cloud Run APIs.  

Success = running on synthetic data, HIPAA-aware, with a working demo flow and clear checkpoints.

## HIPAA Checkpoints
- CMEK on Pub/Sub, GCS, BigQuery  
- Least-privilege IAM, audit logs enabled  
- No PHI in logs, TLS enforced  
- Append-only `session_events` table

## Synthetic Dataset
- Therapist: **TherapistA**  
- Patient: **PatientX**  
- 5 short messages across themes: *work, anxiety, finances, sleep, hope*  
- Each message tagged with a sentiment (*positive, negative, neutral*)  
- Example file: `docs/synthetic/seed.jsonl`

## Output Flow Checklist
- Pub/Sub topic (Avro schema)  
- Dataflow pipeline: clean + validate  
- GCS buckets (raw + processed)  
- Composer DAGs  
- BigQuery tables: `session_events`, `message_analytics`, `session_summaries`, `therapist_licenses`  
- Vertex AI: Gemini Flash for summaries & sentiment  
- Cloud Run services: Summaries + License Verify

## Free-tier Budget Notes
- Dataflow: 1 worker, ≤15 min runtime  
- BigQuery: under 1TB queries / 10GB storage free  
- Vertex AI: ≤10 calls/day  
- Cloud Run: within free tier (2M requests/month)  
- DCA API: free

## Full Flow (MVP)
Patient message → **Pub/Sub** → **Dataflow (clean/validate)** → **GCS (raw + staging)** → **Composer DAG** → **BigQuery** (`session_events`) →  
**Analytics job** → **Vertex AI (themes + sentiment)** → **BigQuery** (`message_analytics`) →  
**Summary API (Cloud Run)** → **Vertex AI (summary)** → **BigQuery** (`session_summaries`) →  
**License Verify API (Cloud Run)** → **CA DCA search** → **BigQuery** (`therapist_licenses`)

## California Therapist License Verification (DCA)

**What it is**  
California’s Department of Consumer Affairs (DCA) provides a public license search to confirm a therapist’s license status. We hit it **server-side** and **only at onboarding / explicit re-check**, then cache the result.

**Endpoint**  
- Public search site: `https://search.dca.ca.gov`  
- Query it from a Cloud Run service (no client-side calls), parse the result, normalize status, and cache.

**When we call it**  
- **Registration:** required check before completing signup.  
- **Login:** background re-check if cache is stale (e.g., >30 days).  
- **Profile:** optional “Recheck license” button.

**Integration flow (server)**  
1) Client → `GET /verify?therapist_id=TherapistA&license_id=<CA_LICENSE>` (Cloud Run).  
2) Service looks in BigQuery cache `therapist_licenses`.  
3) If fresh → return cached result.  
4) Else → fetch from `search.dca.ca.gov`, normalize → upsert cache → return result.

**Cache table (BigQuery)**  
`therapist_licenses( therapist_id STRING, license_id STRING, status STRING, status_detail STRING, last_checked TIMESTAMP )`  
- `status ∈ {ACTIVE, INACTIVE, EXPIRED, SUSPENDED, UNKNOWN}`  
- TTL or periodic refresh to keep it current.

**Example response**  
```json
{
  "therapist_id": "TherapistA",
  "license_id": "CA-ABC12345",
  "status": "ACTIVE",
  "status_detail": "Active - clear",
  "last_checked": "2025-08-17T17:20:05Z",
  "source": "dca_cache"
}
```

## Output Flow Requirements 

**Event schema (Avro over Pub/Sub):**
- `session_id STRING`
- `therapist_id STRING`
- `patient_id STRING`
- `ts TIMESTAMP (millis)`
- `text STRING?`
- `audio_uri STRING?`
- `source STRING` (default: "patient-app")
- `ingest_id STRING` (idempotency key added in Dataflow)

**GCS buckets:**
- `raw-audio` (CMEK, uniform access)
- `staging-events` (CMEK, uniform access)

**BigQuery dataset:** `thera_poc` (CMEK, partitioned tables)

**Tables & keys:**
- `session_events`
  - `session_id STRING`, `therapist_id STRING`, `patient_id STRING`, `ts TIMESTAMP`, `text STRING`, `audio_uri STRING`, `ingest_id STRING`
  - Partition: `DATE(ts)`; **primary dedupe key**: (`session_id`, `ts`, `ingest_id`)
- `message_analytics`
  - `week_start DATE`, `session_id STRING`, `theme STRING`, `sentiment STRING`, `message_count INT64`
  - Partition: `week_start`
- `session_summaries`
  - `session_id STRING`, `summary STRING`, `model STRING`, `created_at TIMESTAMP`
  - Partition: `DATE(created_at)`
- `therapist_licenses`
  - `therapist_id STRING`, `license_id STRING`, `status STRING`, `last_checked TIMESTAMP`

**Composer DAG (outline):**
1. Trigger Dataflow job (reads Pub/Sub Avro, validates, writes to GCS).
2. Convert Avro→JSON (lightweight task) into `staging-events`.
3. Load to BigQuery `session_events` with dedupe on `ingest_id`.
4. Log success/failure; alert on retries.

