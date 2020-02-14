import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

import boto3
import sagemaker
import yaml
from boto3.session import Session
from sagemaker.chainer.estimator import Chainer
from sagemaker.pytorch.estimator import PyTorch
from sagemaker.tensorflow.estimator import TensorFlow
from sagemaker.tuner import (
    CategoricalParameter,
    ContinuousParameter,
    HyperparameterTuner,
    IntegerParameter,
)

hp_type = {
    "continuous": ContinuousParameter,
    "integer": IntegerParameter,
    "categorical": CategoricalParameter,
}


class FrameworkName:
    Chainer = "ch"
    TensorFlow = "tf"
    PyTorch = "pt"

    values = [
        PyTorch,
        TensorFlow,
        Chainer,
    ]


def exec_training_sm(
    session, client, job_name, conf, framework_name, max_parallel_jobs
):
    sagemaker_session = sagemaker.Session(
        boto_session=session, sagemaker_client=client
    )

    # input data
    inputs = conf["inputs"]

    if "upload_data" in conf and isinstance(conf["upload_data"], list):
        for d in conf["upload_data"]:
            s3_dir = sagemaker_session.upload_data(
                path=d["path"],
                key_prefix=os.path.join(job_name, d["key_prefix"]),
            )
            inputs[d["name"]] = s3_dir

    estimator_args = conf["estimator"]
    estimator_args["sagemaker_session"] = sagemaker_session

    hyperparameters = estimator_args.pop("hyperparameters")
    fixed, targets = {}, {}
    for k, v in hyperparameters.items():
        if isinstance(v, dict):
            targets[k] = v
        else:
            fixed[k] = v
    estimator_args["hyperparameters"] = fixed

    if framework_name == FrameworkName.PyTorch:
        estimator = PyTorch(**estimator_args)
    elif framework_name == FrameworkName.TensorFlow:
        estimator = TensorFlow(**estimator_args)
    elif framework_name == FrameworkName.Chainer:
        estimator = Chainer(**estimator_args)

    if len(targets) == 0:
        estimator.fit(inputs, wait=False, job_name=job_name)
    else:
        if "tuner" in conf:
            tuner_args = conf["tuner"]
            hyperparameter_ranges = {}
            for k, v in targets.items():
                hyperparameter_ranges[k] = hp_type[v["type"].lower()](
                    v["range"]
                )
        else:  # use default values
            tuner_args = {
                "objective_metric_name": "metric_name",
                "metric_definitions": [
                    {"Name": "metric_name", "Regex": "ignore"}
                ],
                "strategy": "Random",
                "objective_type": "Maximize",
                "early_stopping_type": "Off",
            }
            max_jobs = 1
            hyperparameter_ranges = {}
            for k, v in targets.items():
                if v["type"].lower() != "categorical":
                    raise ValueError(
                        "the default tuner only supports Categorigal params."
                    )
                max_jobs *= len(v["range"])
                hyperparameter_ranges[k] = hp_type[v["type"].lower()](
                    v["range"]
                )
            tuner_args["max_jobs"] = max_jobs

        tuner_args["estimator"] = estimator
        tuner_args["hyperparameter_ranges"] = hyperparameter_ranges
        tuner_args["max_parallel_jobs"] = max_parallel_jobs
        tuner_args["base_tuning_job_name"] = job_name
        tuner_args["warm_start_config"] = None  # not supported yet.

        tuner = HyperparameterTuner(**tuner_args)
        tuner.fit(inputs, job_name=job_name)


def exec_training_local(conf, pytorch):
    if pytorch:
        raise NotImplementedError

    estimator_args = conf["estimator"]
    inputs = conf["inputs"]

    source_dir = estimator_args["source_dir"]
    hyperparameters = estimator_args["hyperparameters"]
    entry_point = estimator_args["entry_point"]

    for inp_name in inputs.keys():
        env_var_name = f"SM_CHANNEL_{inp_name.upper()}"
        assert env_var_name in os.environ, f"{env_var_name} doesn't exist."

    cmd = ["python", str(Path(source_dir) / entry_point)]
    for k, v in hyperparameters.items():
        k = "--{}".format(k)
        cmd.append(k)
        cmd.append(str(v))

    print()
    print("Invoked the following command:")
    print(" ".join(cmd))
    print()
    subprocess.call(cmd)


def exec_training(args):
    conf = yaml.load(Path(args.setting).open(), Loader=yaml.SafeLoader)

    if args.local:
        exec_training_local(conf, args.pytorch)
    else:
        job_name = args.job_name or "{}-{}".format(
            Path(args.setting).stem.replace("_", "-"),
            datetime.now().strftime("%s"),
        )

        profile_name = args.profile_name or conf.get("profile_name")
        if profile_name is None:
            session = Session()
            client = boto3.client("sagemaker", region_name=session.region_name)
        else:
            session = Session(profile_name=profile_name)
            credentials = session.get_credentials()

            client = boto3.client(
                "sagemaker",
                region_name=session.region_name,
                aws_access_key_id=credentials.access_key,
                aws_secret_access_key=credentials.secret_key,
                aws_session_token=credentials.token,
            )

        exec_training_sm(
            session,
            client,
            job_name,
            conf,
            args.pytorch,
            args.max_parallel_jobs,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("setting", type=str, help="Path to setting file.")
    parser.add_argument(
        "--job_name",
        "-j",
        type=str,
        help="Training job name. It must be unique.",
    )
    parser.add_argument(
        "--profile_name",
        "-p",
        type=str,
        default=None,
        help="When execute a training from local, enter the profile name.",
    )
    parser.add_argument(
        "--framework_name",
        "-f",
        choices=FrameworkName.values,
        default=FrameworkName.Chainer,
        help="pt: pytorch, ch: chainer, tf: tensorflow",
    )
    parser.add_argument(
        "--max_parallel_jobs",
        type=int,
        default=1,
        help="# wokers for bulk training.",
    )
    parser.add_argument(
        "--local", "-l", action="store_true", help="local excution"
    )
    args = parser.parse_args()
    exec_training(args)
