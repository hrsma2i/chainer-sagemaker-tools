import os
from pathlib import Path

import boto3
import botocore
from moto import mock_s3
from pytest_mock import MockFixture
from ignite.engine import Engine

from smtools.torch.handlers import s3_copy


@mock_s3
def test_s3_copy(tmp_path: Path, mocker: MockFixture):
    # Setup
    # local files to upload
    names = ["model.tar.gz", "trainer_checkpoint_123.pth", "log.sqlite"]
    for name in names:
        (tmp_path / name).write_text(f"This is {name}.")

    # trainer mock
    trainer = mocker.MagicMock(spec=Engine)
    trainer.iteration = 123

    # S3 bucket mock
    s3 = boto3.resource("s3")
    bucket_name = "sample"
    s3.create_bucket(Bucket=bucket_name)

    # Excute
    s3_copy(
        trainer,
        pattern=f"{tmp_path}/model.tar.gz",
        bucket_name=bucket_name,
        key_prefix="{job_name}/model/iter_{trainer.iteration}",
    )
    s3_copy(
        trainer,
        pattern=f"{tmp_path}/trainer_checkpoint_*.pth",
        bucket_name=bucket_name,
        key_prefix="{job_name}/trainer/iter_{trainer.iteration}",
    )
    s3_copy(
        trainer, pattern=f"{tmp_path}/log.sqlite", bucket_name=bucket_name,
    )

    # Check
    try:
        # res = s3.Object(bucket_name, "model/iter_123/model.tar.gz").get()
        bucket = s3.Bucket(bucket_name)
        object_summaries = bucket.objects.all()
        keys = tuple(sorted([obj_sum.key for obj_sum in object_summaries]))
        job_name = os.uname()[1]
        assert keys == tuple(
            sorted(
                [
                    f"{job_name}/model/iter_123/model.tar.gz",
                    f"{job_name}/trainer/iter_123/trainer_checkpoint_123.pth",
                    f"{job_name}/log.sqlite",
                ]
            )
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            assert False, "The file doesn't exist."
        else:
            assert False, e
