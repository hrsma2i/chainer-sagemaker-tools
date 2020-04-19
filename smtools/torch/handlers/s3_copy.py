import os
import json
from pathlib import Path

import boto3
from ignite.engine import Engine


def s3_copy(
    trainer: Engine,
    pattern: str,
    bucket_name: str,
    key_prefix: str = "{job_name}",
):
    try:
        training_env = os.environ["SM_TRAINING_ENV"]
        job_name = json.loads(training_env)["job_name"]
    except Exception:
        job_name = os.uname()[1]

    paths = list(Path("/").glob(pattern.lstrip("/")))

    s3 = boto3.resource("s3")
    key_prefix = key_prefix.format(job_name=job_name, trainer=trainer)
    for path in paths:
        s3.meta.client.upload_file(
            Filename=str(path),
            Bucket=bucket_name,
            Key=f"{key_prefix}/{path.name}",
        )
