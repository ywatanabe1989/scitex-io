#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Format handler registry for scitex-io.

Two-tier registry: built-in handlers (lower priority) and user-registered
handlers (higher priority). Users and upstream packages (e.g., scitex with
.pltz/.figz/.statsz) register custom handlers via the same API.

Example
-------
>>> from scitex_io import register_saver, register_loader, save, load
>>>
>>> @register_saver(".custom")
... def save_custom(obj, path, **kw):
...     with open(path, "w") as f:
...         f.write(str(obj))
>>>
>>> @register_loader(".custom")
... def load_custom(path, **kw):
...     with open(path) as f:
...         return f.read()
>>>
>>> save("hello", "/tmp/test.custom")
>>> load("/tmp/test.custom")
'hello'
"""

from typing import Callable, Dict, List, Optional

# Two-tier registries
_builtin_savers: Dict[str, Callable] = {}
_builtin_loaders: Dict[str, Callable] = {}
_user_savers: Dict[str, Callable] = {}
_user_loaders: Dict[str, Callable] = {}


def _normalize_ext(ext: str) -> str:
    """Normalize extension to include leading dot."""
    ext = ext.strip()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext.lower()


def register_saver(ext: str, fn: Callable = None, *, builtin: bool = False):
    """Register a save handler for a file extension.

    Can be used as a decorator or called directly::

        @register_saver(".json")
        def my_json_saver(obj, path, **kwargs): ...

        register_saver(".json", my_json_saver)

    Parameters
    ----------
    ext : str
        File extension (e.g., ".json", "json" — dot is optional).
    fn : Callable, optional
        Handler function ``(obj, path, **kwargs) -> None``.
        If None, returns a decorator.
    builtin : bool
        If True, registers as built-in (lower priority).
        User registrations always override built-ins.
    """
    ext = _normalize_ext(ext)
    registry = _builtin_savers if builtin else _user_savers

    if fn is not None:
        registry[ext] = fn
        return fn

    def decorator(func):
        registry[ext] = func
        return func

    return decorator


def register_loader(ext: str, fn: Callable = None, *, builtin: bool = False):
    """Register a load handler for a file extension.

    Same API as :func:`register_saver`.

    Parameters
    ----------
    ext : str
        File extension (e.g., ".json", "json" — dot is optional).
    fn : Callable, optional
        Handler function ``(path, **kwargs) -> Any``.
    builtin : bool
        If True, registers as built-in (lower priority).
    """
    ext = _normalize_ext(ext)
    registry = _builtin_loaders if builtin else _user_loaders

    if fn is not None:
        registry[ext] = fn
        return fn

    def decorator(func):
        registry[ext] = func
        return func

    return decorator


def get_saver(ext: str) -> Optional[Callable]:
    """Look up a save handler. User overrides take priority."""
    ext = _normalize_ext(ext)
    return _user_savers.get(ext) or _builtin_savers.get(ext)


def get_loader(ext: str) -> Optional[Callable]:
    """Look up a load handler. User overrides take priority."""
    ext = _normalize_ext(ext)
    return _user_loaders.get(ext) or _builtin_loaders.get(ext)


def list_formats() -> Dict[str, Dict[str, List[str]]]:
    """List all registered formats.

    Returns
    -------
    dict
        ``{"save": {"builtin": [...], "user": [...]},
          "load": {"builtin": [...], "user": [...]}}``
    """
    return {
        "save": {
            "builtin": sorted(_builtin_savers.keys()),
            "user": sorted(_user_savers.keys()),
        },
        "load": {
            "builtin": sorted(_builtin_loaders.keys()),
            "user": sorted(_user_loaders.keys()),
        },
    }


def unregister_saver(ext: str) -> bool:
    """Remove a user-registered saver. Returns True if found."""
    ext = _normalize_ext(ext)
    return _user_savers.pop(ext, None) is not None


def unregister_loader(ext: str) -> bool:
    """Remove a user-registered loader. Returns True if found."""
    ext = _normalize_ext(ext)
    return _user_loaders.pop(ext, None) is not None
