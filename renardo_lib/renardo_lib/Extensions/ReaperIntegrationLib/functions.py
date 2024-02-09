from typing import Tuple


def make_snake_name(name: str) -> str:
    return name.lower().replace(' ', '_').replace('/', '_').replace('(', '_').replace(':', '_').replace('__','_').replace('-','_')


def split_param_name(name) -> Tuple[str, str]:
    if name == make_snake_name(name):
        splitted = name.split('_')
        reaobject_name = splitted[0]
        param_name = '_'.join(splitted[1:])
        return reaobject_name, param_name
    else:
        raise KeyError("Parameter name not snake_case :" + name)


