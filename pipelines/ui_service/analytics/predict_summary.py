import argparse
import json
from google.cloud import storage
from vertexai.preview.language_models import TextGenerationModel
import vertexai


def init_vertex_ai(project: str, region: str):
    vertexai.init(project=project, location=region)
    print(f"Vertex AI initialized for project '{project}' in region '{region}'")


def read_input_file(input_uri: str) -> list:
    """Reads a JSONL file from GCS and returns a list of inputs"""
    client = storage.Client()
    bucket_name, blob_path = input_uri.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    data = blob.download_as_text().splitlines()
    print(f"Loaded {len(data)} lines from {input_uri}")
    return [json.loads(line) for line in data]


def write_output_file(output_uri: str, responses: list):
    """Writes list of summaries to a GCS .jsonl file"""
    bucket_name, blob_path = output_uri.replace("gs://", "").split("/", 1)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    lines = [json.dumps(r) for r in responses]
    blob.upload_from_string("\n".join(lines))
    print(f"Wrote {len(responses)} results to {output_uri}")


def summarize_texts(texts: list) -> list:
    """Calls Gemini Flash to summarize each input text"""
    model = TextGenerationModel.from_pretrained("gemini-1.5-flash")
    responses = []
    for item in texts:
        raw_text = item.get("text") or item.get("content") or str(item)
        prompt = f"Summarize this therapist session:\n\n{raw_text}"
        try:
            result = model.predict(prompt, temperature=0.2)
            responses.append({"input": raw_text, "summary": result.text})
        except Exception as e:
            responses.append({"input": raw_text, "error": str(e)})
    return responses


def main(project, region, input_uri, output_uri):
    init_vertex_ai(project, region)
    input_data = read_input_file(input_uri)
    results = summarize_texts(input_data)
    write_output_file(output_uri, results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--input_uri", required=True, help="Format: gs://bucket/input.jsonl")
    parser.add_argument("--output_uri", required=True, help="Format: gs://bucket/output.jsonl")
    args = parser.parse_args()

    main(args.project, args.region, args.input_uri, args.output_uri)
