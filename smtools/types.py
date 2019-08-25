import json


def chainer_trigger(s):
    n, unit = s[:-1], s[-1]
    unit_name = {"e": "epoch", "i": "iteration"}
    assert (
        unit in unit_name
    ), "The last character of a trigger must be `e` or `i`"
    return [int(n), unit_name[unit]]


def list_from_str(s):
    if type(s) == list:
        return s
    elif type(s) == str:
        try:
            return json.loads(s.replace("'", '"'))
        except ValueError:
            return s
    else:
        raise ValueError
