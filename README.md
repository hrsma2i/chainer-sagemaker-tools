# chainer-sagemaker-tools

This repository is a collection of tools to run SageMaker jobs.

It contains

- CLIs : Some command line tools to use SageMaker easily. See below guidelines.
- ~~[`sage_extensions`](./sage_extensions) : Some Extensions for Chainer Trainer.~~ → Use `smtools.extensions`, but keep this package to reflect the original repository's update.
- [`smtools`](./smtools) : Utilities and Chainer extensions modified by hrsma2i.

# Table of contents

- [Installation](#Installation)
- [Run SageMaker training jobs](#Run-SageMaker-training-jobs)
- [Deploy trained model](#Deploy-trained-model)
- [Run batch inference](#Run-batch-inference)
- [Config management example](#Config-management-example)

# Installation

```bash
$ git clone https://github.com/tn1031/chainer-sagemaker-tools.git
$ cd chainer-sagemaker-tools
$ pip install .
```

When installing to the ML instances, since installing to them is based on the contents of `requirements.txt` , it is necessary to contain the below line on `requirements.txt`.

```
git+https://github.com/tn1031/chainer-sagemaker-tools.git
```

Then put the file in the `source_dir` .

# Run SageMaker training jobs

`smtrain` is a command line tool to run SageMaker training jobs.

### Usage

```bash
$ smtrain {path_to_setting} [-j {job_name} -p {aws_profile_name} -l]
```

- `path_to_setting` - Path to the setting file. The format of this file is described in [here](examples/train.yml).
- `job_name` - Training job name. It must be unique in the same AWS account. Its default is `{setting_name}-{unixtime}`.
- `aws_profile_name` - The name of profile that are stored in `~/.aws/config` . You can also designate this from the setting file with the key `profile_name`.
- `-l`, `--local`: Excute the entry point on the local machine for efficient debugging.

# Deploy trained model

`smdeploy` is a command line tool to deploy.

### Usage

```bash
$ smdeploy <endpoint_name> <path_to_setting> [-p <aws_profile_name>]
```

- `endpoint_name` - Endpoint name.
- `path_to_setting` - Path to the setting file. The format of this file is described in [here](https://github.com/tn1031/chainer-sagemaker-tools/blob/master/examples/deploy.yml).
- `aws_profile_name` - The name of profile that are stored in `~/.aws/config` .

# Run batch inference

`smbatch` is a command line tool to run batch inference.

### Usage

```bash
$ smbatch <model_name> <path_to_setting> [-p <aws_profile_name>]
```

- `model_name` - Model name which used for inference.
- `path_to_setting` - Path to the setting file. The format of this file is described in [here](https://github.com/tn1031/chainer-sagemaker-tools/blob/master/examples/batch.yml).
- `aws_profile_name` - The name of profile that are stored in `~/.aws/config` .

# Config management example

There are 4 types of contents in [config files](examples/train.yml).

|        | private                               | public                                                         |
| :----: | :-----------------------------------: | :------------------------------------------------------------: |
| global | role (AWS IAM role) <br> profile_name | train_instance_type <br> train_volume_size <br> source_dir ... |
| local  | inputs (S3 URI)                       | hyperparameters ...                                            |

We want to track **public** ones and don't want to track **private** ones using git.

We want to share **global** ones among all jobs.

We can do that if we split them into different files and merge them when feeding it to `smtrain`, `smdeploy`, or `smbatch`.


### Example

directory structure

```
settings/
├── global_train.yml
├── global_batch.yml
├── {job1}.yml
├── {job2}.yml
├── ...
├── debug.yml
├── private
│   ├── global.yml
│   ├── {dataset1}.yml
│   ├── {dataset2}.yml
│   └── ...
├── train # public
│   ├── global.yml
│   ├── {model1}.yml
│   ├── {model2}.yml
│   └── ...
├── deploy # public
│   ├── global.yml
│   ├── {model1}.yml
│   ├── {model2}.yml
│   └── ...
└── batch # public
    ├── global.yml
    ├── batch-{model1}-{dataset1}.yml
    ├── batch-{model1}-{dataset2}.yml
    └── ...
```

`.gitignore`

```
settings/*
!settings/train
!settings/deploy
!settings/batch
```


`settings/private/global.yml`

```yml
estimator:
  role: # {AWS IAM role}
  profile_name: # {AWS profile name}
  hyperparameters:
    hook: # {slack hook for slack_reporter}
    channel: # {slack channel for slack_reporter}
```


`settings/private/{dataset1}.yml`

```yml
inputs:
  # SM_CHANNEL_LABEL_DIR
  label_dir: 's3://{bucket}/.../{dataset1}/main/labels'
  # SM_CHANNEL_IMAGE_DIR
  image_dir: 's3://{bucket}/.../{dataset1}/main/images'
```


`settings/train/global.yml`

```yml
upload_data:
  # There are config yaml files for entry ponits.
  # Can access this dir on SageMake using SM_CHANNER_CONFIG_DIR
  - path: 'configs'
    key_prefix: 'config'
    name: 'config_dir'

# Parameters for the Estimator constructor.
estimator:
  source_dir: 'src'
  input_mode: 'File'
  use_mpi: False
  train_instance_count: 1
  train_instance_type: 'ml.p2.xlarge'
  train_volume_size: 30
  train_max_run: 432000  # 5 * 24 * 60 * 60
  framework_version: '5.0.0'
  hyperparameters:
    use_sagemaker: 1
    hook: # {slack hook for slack_reporter}
    channel: # {slack channel for slack_reporter}
```


`settings/train/{model1}.yml`

```yml
estimator:
  entry_point: 'train_{model1}.py'
  hyperparameters:
    yml_file: '{model1}.yml'
    epochs: 10
    batch-size: 64
```


`settings/debug.yml`

```yml
estimator:
  hyperparameters:
    epochs: 1 # overwrite with this value
    batch-size: 2 # overwrite with this value

inputs:
  # SM_CHANNEL_LABEL_DIR
  label_dir: 's3://{bucket}/.../{dataset1}/tiny/labels'
  # SM_CHANNEL_IMAGE_DIR
  image_dir: 's3://{bucket}/.../{dataset1}/tiny/images'
```

Merge configs in `settigns/`.

```sh
mgconf \
  private/global.yml \
  train/global.yml \
  -o global_train.yml

mgconf \
  global_train.yml \
  private/{dataset1}.yml \
  train/{model1}.yml \
  -o {job1}.yml

mgconf {job1}.yml \
  debug.yml \
  -o debug-{job1}.yml
```

Excute jobs using the merged configs.

```
smtrain settings/debug-{job1}.yml

smtrain settings/{job1}.yml
```

