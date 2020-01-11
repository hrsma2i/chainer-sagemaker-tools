# Chainer Extensions

- [`slack_report`](#slack_report) : Trainer extension to post training metrics and plots.
- [`snapshot_transfer`](#snapshot_transfer) : Trainer extension to copy latest snapshots and other outputs.

## slack_report

### Python code example

```python
from smtools.extensions import slack_report

val_interval = 1, 'epoch'
keys = ['iteration', 'epoch', 'elapsed_time', 'lr',
         'main/loss', 'validation/main/loss',
         'main/accuracy', 'validation/main/accuracy']
hook = '<webhook_url>'
channel = '<slack_channel_name>'
pretext = 'Train cifar using VGG16'
public_bucket_name = '<s3_bucket_name>'

trainer.extend(
    slack_report(keys,
                 hook,
                 channel,
                 pretext,
                 public_bucket_name),
    trigger=val_interval)
```

### Parameter

- `keys` - Keys of values to display. 
- `hook` - Incoming webhook url.
- `channel` - Slack channel to post.
- `pretext` - Any string. This value is shown as pretext attatchment of the slack post. The default value is `None` .
- `public_bucket_name` - S3 bucket name to put plots. If it is `None` , the plot reports don't be posted.
- `region` - Region name.

## snapshot_transfer

This extension compresses some files in `trainer.out` such as the latest snapshot and the log and copies it to S3.
The distination is `s3://{buket_name}/{job_name}/snapshot/{key_prefix}/model.tar.gz`.
Its default is `s3://{dafault_bucket}/{job_name}/snapshot/iter_{iteration:09}/model.tar.gz`
This uri is the similar to the path to put the `sourcedir.tar.gz` .

### Python code example

```python
from smtools.extensions import snapshot_transfer

snapshot_trigger = 1, 'epoch'
patterns = [
    "weight.npz",
    "log",
    "last_trainer_snapshot",
    "args.yml",
]

trainer.extend(
    snapshot_transfer(patterns, trigger=snapshot_trigger)
```

### Parameter

- `patterns` - Prefixes of files to copy. Each of the latest file whose name contains the one of the given prefix list is transferred to S3.