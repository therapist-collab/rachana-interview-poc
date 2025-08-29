import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions
from apache_beam.transforms.window import FixedWindows
from datetime import timedelta
import apache_beam.io.fileio as fileio
import uuid
import json

class ParsePubSubMessage(beam.DoFn):
    def process(self, element):
        row = json.loads(element)
        yield json.dumps(row)  # convert back to string for text sink

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--input_topic', required=True)
    parser.add_argument('--output_path', required=True)
    known_args, pipeline_args = parser.parse_known_args()

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(GoogleCloudOptions).project = known_args.project
    pipeline_options.view_as(GoogleCloudOptions).region = known_args.region
    pipeline_options.view_as(GoogleCloudOptions).job_name = "pubsub-to-gcs"
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=known_args.input_topic)
            | "ParseJSON" >> beam.ParDo(ParsePubSubMessage())
            | "WindowIntoFixed" >> beam.WindowInto(FixedWindows(60))
            | "WriteToGCS" >> fileio.WriteToFiles(
                path=known_args.output_path,
                sink=lambda dest: fileio.TextSink(),
                file_naming=fileio.destination_prefix_naming(suffix=".json")
            )
        )

if __name__ == "__main__":
    run()
