import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import boto3
from chainer.training import extension


def snapshot_transfer(patterns):
    @extension.make_extension(trigger=(1, "epoch"), priority=-200)
    def snapshot_transfer(trainer):
        _snapshot_transfer(trainer, patterns)

    return snapshot_transfer


def _snapshot_transfer(trainer, patterns):
    # [todo] Exception handling
    training_env = os.getenv("SM_TRAINING_ENV")
    module_dir = Path(json.loads(training_env)["module_dir"])
    # module_dir: s3://{bucket_name}/{job_name}/source/sourcedir.tar.gz'
    bucket_name = module_dir.parents[2].name
    job_name = module_dir.parents[1].name
    job_name = json.loads(training_env)["job_name"]

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    targets = [_get_latest_modified_object(trainer.out, k) for k in patterns]

    with tempfile.TemporaryDirectory(dir=trainer.out) as tmp_dir:
        tmp_dir = Path(tmp_dir)
        for src_file in targets:
            if src_file is not None:
                tgt_file = tmp_dir / src_file.name
                shutil.copyfile(str(src_file), str(tgt_file))

        arcname = "model"
        out_tar = (Path(trainer.out) / arcname).with_suffix(".tar.gz")
        with tarfile.open(str(out_tar), mode="w:gz") as tar:
            tar.add(str(tmp_dir), arcname=arcname)

        dst = str(
            Path(job_name)
            / "snapshot"
            / "iter_{.updater.iteration:09}".format(trainer)
            / out_tar.name
        )
        obj = bucket.Object(dst)

        try:
            obj.upload_file(str(out_tar))
        except Exception as e:
            print(e)

        os.remove(str(out_tar))


def _get_latest_modified_object(dirname, key):
    files = [(f, f.stat().st_mtime) for f in Path(dirname).glob(key)]

    if len(files) == 0:
        return None

    latest = sorted(files, key=lambda x: x[1])[-1]
    return latest[0]
