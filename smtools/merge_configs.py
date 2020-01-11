import argparse
import collections
from io import StringIO
from copy import deepcopy
import difflib
from pathlib import Path

import six
import yaml

try:
    from colorama import Fore, Back, Style, init

    init()
except ImportError:  # fallback so that the imported classes always exist

    class ColorFallback:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = ColorFallback()

# python 3.8+ compatibility
try:
    collectionsAbc = collections.abc
except:
    collectionsAbc = collections


SEPARATION = "\n" + "".join(["=" for _ in range(96)]) + "\n"


def nestupdate(d, u):
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collectionsAbc.Mapping):
            d[k] = v
        elif isinstance(v, collectionsAbc.Mapping):
            d[k] = nestupdate(dv, v)
        elif type(v) == list:
            d[k] = list(dv) + v
        else:
            d[k] = v
    return d


def merge_configs(configs, verbose=True, titles=None):
    print()

    if titles is None:
        titles = [f"config-{i+1}" for i in range(len(configs))]

    title = titles[0]
    config = configs[0]
    first_title = deepcopy(title)
    first_config = deepcopy(config)

    for title, _config in zip(titles[1:], configs[1:]):

        config_prev = deepcopy(config)
        config = nestupdate(config, _config)

        if verbose:
            print(
                take_diff(
                    config_prev,
                    config,
                    from_title="previous config",
                    to_title=title,
                )
            )
            print(SEPARATION)

    if verbose:
        print(
            take_diff(
                first_config,
                config,
                from_title=first_title,
                to_title="FINALE CONFIG",
            )
        )

    return config


def merge_configs_from_file(yml_files, out_file=None, verbose=True):
    configs = [
        yaml.load(Path(yml_file).open(), Loader=yaml.SafeLoader)
        for yml_file in yml_files
    ]
    config = merge_configs(configs, titles=yml_files, verbose=verbose)

    if out_file is not None:
        out_file = Path(out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(config, out_file.open("w"), default_flow_style=False)

    return config


def take_diff(from_dict, to_dict, from_title="", to_title=""):
    from_ymlstr = dumps(from_dict, default_flow_style=False).splitlines()
    to_ymlstr = dumps(to_dict, default_flow_style=False).splitlines()
    diff = difflib.unified_diff(
        from_ymlstr, to_ymlstr, fromfile=from_title, tofile=to_title
    )
    diff = color_diff(diff)
    return "\n".join(diff)


def color_diff(diff):
    for line in diff:
        if line.startswith("+"):
            yield Fore.GREEN + line + Fore.RESET
        elif line.startswith("-"):
            yield Fore.RED + line + Fore.RESET
        elif line.startswith("^"):
            yield Fore.BLUE + line + Fore.RESET
        else:
            yield line
    return color_diff


def dumps(d, **kwargs):
    buf = StringIO()
    yaml.dump(d, buf, **kwargs)
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yml_files", nargs="*")
    parser.add_argument("-o", "--out_file")
    args = parser.parse_args()

    merge_configs_from_file(**vars(args))
