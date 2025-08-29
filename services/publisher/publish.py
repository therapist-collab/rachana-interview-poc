import json
import time
import uuid
from google.cloud import pubsub_v1

PROJECT_ID = "rachana-interview-poc"
TOPIC_ID = "thera-session-events"
topic_path = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"

publisher = pubsub_v1.PublisherClient()

seed_messages = [
    {
        "session_id": "s1",
        "therapist_id": "TherapistA",
        "patient_id": "PatientX",
        "ts": int(time.time() * 1000),  # Valid timestamp-millis
        "text": "work was intense today",
        "audio_uri": None,
        "source": "patient-app",
        "ingest_id": f"s1:{int(time.time() * 1000)}"
    },
    {
        "session_id": "s1",
        "therapist_id": "TherapistA",
        "patient_id": "PatientX",
        "ts": int(time.time() * 1000) + 1,
        "text": "feeling anxious about bills",
        "audio_uri": None,
        "source": "patient-app",
        "ingest_id": f"s1:{int(time.time() * 1000) + 1}"
    },
    {
        "session_id": "s1",
        "therapist_id": "TherapistA",
        "patient_id": "PatientX",
        "ts": int(time.time() * 1000) + 2,
        "text": "sleep is better",
        "audio_uri": None,
        "source": "patient-app",
        "ingest_id": f"s1:{int(time.time() * 1000) + 2}"
    },
    {
        "session_id": "s1",
        "therapist_id": "TherapistA",
        "patient_id": "PatientX",
        "ts": int(time.time() * 1000) + 3,
        "text": "a bit more hopeful",
        "audio_uri": None,
        "source": "patient-app",
        "ingest_id": f"s1:{int(time.time() * 1000) + 3}"
    },
    {
        "session_id": "s1",
        "therapist_id": "TherapistA",
        "patient_id": "PatientX",
        "ts": int(time.time() * 1000) + 4,
        "text": "voice note coming later",
        "audio_uri": None,
        "source": "patient-app",
        "ingest_id": f"s1:{int(time.time() * 1000) + 4}"
    }
]

def main():
    for msg in seed_messages:
        data_bytes = json.dumps(msg).encode("utf-8")  # Valid JSON object
        print("Publishing:", json.dumps(msg, indent=2))  # Debug print
        future = publisher.publish(topic_path, data=data_bytes)
        print("Published:", future.result())

if __name__ == "__main__":
    main()
