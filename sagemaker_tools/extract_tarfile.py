import os
from glob import glob
import tarfile
import argparse


def extract_tarfile(inp_dir, remove=True):
    try:
        tar_file = sorted(glob(os.path.join(inp_dir, '*.tar.gz')))[0]
    except IndexError as e:
        print(e)
        print('There is no tar file in {}'.format(inp_dir))
        tar_file = concat(inp_dir, remove=remove)
    extract(tar_file, remove=remove)


def concat(inp_dir, remove=True):
    tar_file_fracs = sorted(glob(os.path.join(inp_dir, '*.tar.gz-*')))
    # '.../dataset.tar.gz-*' -> '.../dataset.tar.gz'
    assert len(tar_file_fracs) > 0,\
        'Cant\'t even find tar file fractions in {}'.format(inp_dir)

    tar_file = os.path.join(
        inp_dir,
        os.path.basename(tar_file_fracs[0]).split('-')[0],
    )

    for frac in tar_file_fracs:
        with open(frac, 'rb') as f_in,\
             open(tar_file, 'ab') as f_out:
            f_out.write(f_in.read())
        if remove:
            os.remove(frac)

    return tar_file


def extract(tar_file, remove=True):
    with tarfile.open(tar_file, 'r:gz') as tf:
        tf.extractall(os.path.dirname(tar_file))
        if remove:
            os.remove(tar_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'inp_dir'
    )
    parser.add_argument(
        '-rm', '--remove',
        action="store_true"
    )
    args = parser.parse_args()
    concat(args.inp_dir, remove=args.remove)
