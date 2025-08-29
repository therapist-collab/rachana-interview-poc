import argparse, json, time
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions

# ---- Avro schema (string) for WriteToAvro ----
AVRO_SCHEMA = {
  "type": "record",
  "name": "PatientMessage",
  "namespace": "therapist.poc",
  "fields": [
    {"name":"session_id","type":"string"},
    {"name":"therapist_id","type":"string"},
    {"name":"patient_id","type":"string"},
    {"name":"ts","type":"long"},  # epoch millis
    {"name":"text","type":["null","string"]},
    {"name":"audio_uri","type":["null","string"]},
    {"name":"source","type":["null","string"]},
    {"name":"ingest_id","type":"string"}  # required after clean step
  ]
}

REQUIRED = ["session_id","therapist_id","patient_id","ts"]  # minimally required

class ParseAndValidate(beam.DoFn):
    def process(self, message_bytes):
        try:
            msg = json.loads(message_bytes.decode("utf-8"))
            # Ensure required keys
            for k in REQUIRED:
                if k not in msg or msg[k] in (None, ""):
                    raise ValueError(f"Missing required field: {k}")

            # Normalize optional fields
            msg["text"] = msg.get("text")
            msg["audio_uri"] = msg.get("audio_uri")
            msg["source"] = msg.get("source", "patient-app")

            # Idempotency: ensure ingest_id (session_id+ts if not provided)
            if not msg.get("ingest_id"):
                msg["ingest_id"] = f"{msg['session_id']}:{msg['ts']}"

            # Ensure ts is long
            if isinstance(msg["ts"], str):
                msg["ts"] = int(msg["ts"])

            yield msg
        except Exception as e:
            yield beam.pvalue.TaggedOutput("dead", {"error": str(e), "payload": message_bytes.decode("utf-8", "ignore")})

def key_by_ingest_id(elem):
    return (elem["ingest_id"], elem)

def drop_key(kv):
    return kv[1]

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--runner", default="DirectRunner")
    parser.add_argument("--temp_location", required=True)
    parser.add_argument("--staging_location", required=True)

    parser.add_argument("--input_topic", required=True)
    parser.add_argument("--output_prefix", required=True)      # gs://.../events/date=YYYYMMDD/part
    parser.add_argument("--deadletter_prefix", required=True)  # gs://.../deadletter/date=YYYYMMDD/part
    args, beam_args = parser.parse_known_args(argv)

    options = PipelineOptions(
        beam_args,
        runner=args.runner,
        project=args.project,
        region=args.region,
        temp_location=args.temp_location,
        staging_location=args.staging_location,
        experiments=["use_runner_v2"],
        save_main_session=True,
    )
    options.view_as(StandardOptions).streaming = True
    options.view_as(SetupOptions).save_main_session = True

    # Dated output (for easy ls & screenshots)
    date_str = time.strftime("%Y%m%d")

    with beam.Pipeline(options=options) as p:
        raw = (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(topic=args.input_topic).with_output_types(bytes)
        )

        parsed = (
            raw
            | "Parse+Validate" >> beam.ParDo(ParseAndValidate()).with_outputs("dead", main="good")
        )
        good = parsed.good
        dead = parsed.dead

        # Idempotency: remove duplicates by ingest_id (global window)
        deduped = (
            good
            | "KeyByIngestId" >> beam.Map(key_by_ingest_id)
            | "RemoveDuplicates" >> beam.RemoveDuplicates()
            | "DropKey" >> beam.Map(drop_key)
        )

        # TODO(silence-trim): In a real run you’d fetch audio_uri and run ffmpeg.
        # For Day 3 POC, we skip audio processing (keep uri in record).

        # Write good events to Avro in GCS
        _ = (
            deduped
            | "WriteGoodAvro" >> beam.io.avroio.WriteToAvro(
                file_path_prefix=f"{args.output_prefix}/date={date_str}/part",
                schema=AVRO_SCHEMA,
                use_fastavro=True,
                file_name_suffix=".avro",
                num_shards=1,
            )
        )

        # Dead-letter to JSONL in GCS
        _ = (
            dead
            | "ToJSON" >> beam.Map(lambda d: json.dumps(d))
            | "WriteDeadLetter" >> beam.io.WriteToText(
                file_path_prefix=f"{args.deadletter_prefix}/date={date_str}/part",
                file_name_suffix=".jsonl",
                num_shards=1,
            )
        )

if __name__ == "__main__":
    run()
