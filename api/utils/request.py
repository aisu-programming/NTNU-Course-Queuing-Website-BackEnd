''' Libraries '''
from flask import request
from functools import wraps
from .response import *



''' Settings '''
__all__ = ["Request"]
type_map = {
    "int" : int,
    "list": list,
    "str" : str,
    "dict": dict,
    "bool": bool,
    "None": type(None)
}



''' Functions '''
class _Request(type):
    def __getattr__(self, content_type):
        def get(*keys, vars_dict={}):
            def data_func(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    data = getattr(request, content_type)
                    if data == None:
                        return HTTPError(f"Unaccepted Content-Type {content_type}", 415)
                    try:
                        # Magic
                        kwargs.update({
                            k: (lambda v: v if t is None or type(v) is t else int(''))
                                (
                                    data.get(
                                        (
                                            lambda s, *t: s + ''.join(map(
                                                str.capitalize, t
                                            ))
                                        )(*filter(bool, k.split('_')))
                                    )
                                )
                            # The part of "[key]: [type]" in '@Request.json("[key]: [type]")'
                            for k, t in [(
                                lambda x: (
                                    x[0], type_map.get(x[1].strip()) if x[1:] else None
                                )
                            )(l.split(':', 1)) for l in keys]
                        })
                    except ValueError:
                        return HTTPError("Requested Value With Wrong Type", 400)
                    kwargs.update({ v: data.get(vars_dict[v]) for v in vars_dict })
                    return func(*args, **kwargs)

                return wrapper

            return data_func

        return get


class Request(metaclass=_Request):
    pass