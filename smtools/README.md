# Table of Contents

- [merge_configs](#merge_configs)
- [extract_tarfile](#extract_tarfile)
- [types](#types)
- [extensions](./extensions)

# merge_configs

This module merges config dicts loaded from yaml files for entry point scripts or `smtrain` command.

It takes a list of dicts and iteratively merges them, overwriting each dict by the next dict.

It also shows the difference between the previous config dict and the updated config dict.

This module can be used as a CLI and called from other python scripts.

## Use as a CLI

```sh
mgconf {yml_file1} {yml_file2} ... [-o {out_file}]
```

- `yml_file*`: yaml files to merge.
- `out_file`: The path to save the final merged dict.

### Example

```sh
mgconf configs/bilstm.yml configs/bilstm_fxcnn_st2_poly_cr.yml configs/bilstm_s2s_st2_poly_cr.yml 
```

The above command shows the following colored result.

<details>
<summary>result</summary>

```
--- previous config

+++ ~/bilstm-chainer/configs/bilstm_fxcnn_st2_poly_cr.yml

@@ -1,16 +1,25 @@

 batch_size: 8
 config_model:
   cnn_weight_filename: pretrained_inception_v3
+  config_img_embed:
+    cnn_weight_file: ../models/pretrained_inception_v3
+  config_rnn:
+    dropout_ratio: 0.3
+    n_layers: 2
   emb_size: 512
   init_scale: 0.08
   l2_normalize: false
   rnn_dropout_ratio: 0.3
   rnn_n_stacked: 1
   use_eos: true
-fix_cnn: false
+fix_cnn: true
 fix_fc: false
 init_lr: 0.2
 json_filename_train: train_no_dup.json
 json_filename_valid: valid_no_dup.json
-keep_aspect: false
+json_files_train:
+- ../data/shared/MarylandPolyvore/label/train_cr_my.json
+json_files_valid:
+- ../data/shared/MarylandPolyvore/label/valid_cr_my.json
+keep_aspect: true
 lr_schedule: exponential

================================================================================================

--- previous config

+++ ~/bilstm-chainer/configs/bilstm_s2s_st2_poly_cr.yml

@@ -12,8 +12,10 @@

   rnn_dropout_ratio: 0.3
   rnn_n_stacked: 1
   use_eos: true
+  weight_file_siamese: ../models/siamese_hinge_dot_m1870/weight_iter_000004400
+  yml_file_siamese: ../params/siamese_hinge_dot_m1870.yml
 fix_cnn: true
-fix_fc: false
+fix_fc: true
 init_lr: 0.2
 json_filename_train: train_no_dup.json
 json_filename_valid: valid_no_dup.json

================================================================================================

--- ~/bilstm-chainer/configs/bilstm.yml

+++ FINALE CONFIG

@@ -1,16 +1,27 @@

 batch_size: 8
 config_model:
   cnn_weight_filename: pretrained_inception_v3
+  config_img_embed:
+    cnn_weight_file: ../models/pretrained_inception_v3
+  config_rnn:
+    dropout_ratio: 0.3
+    n_layers: 2
   emb_size: 512
   init_scale: 0.08
   l2_normalize: false
   rnn_dropout_ratio: 0.3
   rnn_n_stacked: 1
   use_eos: true
-fix_cnn: false
-fix_fc: false
+  weight_file_siamese: ../models/siamese_hinge_dot_m1870/weight_iter_000004400
+  yml_file_siamese: ../params/siamese_hinge_dot_m1870.yml
+fix_cnn: true
+fix_fc: true
 init_lr: 0.2
 json_filename_train: train_no_dup.json
 json_filename_valid: valid_no_dup.json
-keep_aspect: false
+json_files_train:
+- ../data/shared/MarylandPolyvore/label/train_cr_my.json
+json_files_valid:
+- ../data/shared/MarylandPolyvore/label/valid_cr_my.json
+keep_aspect: true
 lr_schedule: exponential

```

</details>


## Call from other python scripts

### Example

```py
from merge_configs import merge_configs

configs = # list of config dicts
config = merge_configs(configs, verbose=False)
```

- `verbose=False`: Turn off showing the above result.

# extract_tarfile

### Example

```py
from extract_tarfile import extract_tarfile

inp_dir = # input directory where there is a tar.gz file or split tar.gz-* files.
extract_tarfile(inp_dir, remove=True)
```

The `tar.gz` file or split `tar.gz-*` files in `inp_dir` are extracted to `inp_dir`.

- `remove=True`: Remove split `tar.gz-*` files for memory efficiency.

# types

This module helps `smtrain` pass arguments to an entry point
by setting functions in this module to argparse's type.

SageMaker doesn't support multiple argument options like `--option arg1 arg2`, 
but you can with `list_from_str`.

`chainer_trigger` helps to pass a trigger of Chainer extension like `(100, "iteration")`, `(10, "epoch")`, etc.

### Example

entry point

```py
import argparse

from smtools.types import list_from_str, chainer_trigger

parser = argparse.ArgumentParser()
parser.add_argument("--option", type=list_from_str)
parser.add_argument("--snapshot_interval", type=chainer_trigger)
```

setting.yml

```yml
estimator:
  hyperparameters:
    option:
      - arg1
      - arg2
    snapshot_interval: "100i"
```
