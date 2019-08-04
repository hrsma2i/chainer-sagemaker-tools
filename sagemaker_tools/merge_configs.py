import argparse
import collections
import pprint as pp
import sys
from pathlib import Path

import six
import yaml

# python 3.8+ compatibility
try:
    collectionsAbc = collections.abc
except:
    collectionsAbc = collections


BLUE = '\x1B[34m'
GREEN = '\x1B[32m'
CLEAR = '\x1B[0m'


def nestupdate(d, u, verbose=False, indent=0):
    _indent = ''.join([' ' for _ in range(indent)])
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collectionsAbc.Mapping):
            if verbose and dv != v:
                _k = BLUE + k + CLEAR
                print('{}{}: {} -> {}'.format(_indent, _k, dv, v))
            d[k] = v
        elif isinstance(v, collectionsAbc.Mapping):
            if verbose and dv != v:
                print('{}{}: {{'.format(_indent, k))
            d[k] = nestupdate(dv, v, verbose=verbose, indent=indent+2)
            if verbose and dv != v:
                print('}')
        elif type(v) == list:
            d[k] = list(dv) + v
            if verbose and dv != v:
                _k = BLUE + k + CLEAR
                print('{}{}: {} -> {}'.format(
                    _indent, _k, list(dv), pp.pformat(d[k], indent=2)))
        else:
            if verbose and dv != v:
                _k = BLUE + k + CLEAR
                print('{}{}: {} -> {}'.format(_indent, _k, None, v))
            d[k] = v
    return d


def merge_config(yml_files, out_file=None, verbose=True):
    print()

    setting = dict()
    first = True
    for sf in yml_files:
        if verbose and not first:
            print(GREEN + sf + CLEAR)

        sf = Path(sf)
        _setting = yaml.load(sf.open())
        setting = nestupdate(
            setting, _setting,
            verbose=verbose and not first)

        if verbose and not first:
            print()
        first = False

    if verbose:
        print(GREEN + 'FINAL CONFIG:' + CLEAR)
    pp.pprint(setting, indent=2)

    if out_file is not None:
        out_file = Path(out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(setting, out_file.open('w'), default_flow_style=False)

    return setting


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('yml_files', nargs='*')
    parser.add_argument('-o', '--out_file')
    args = parser.parse_args()

    merge_config(**vars(args))
