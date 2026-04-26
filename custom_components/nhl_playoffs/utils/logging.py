from __future__ import annotations

from . import __name__ as pkg_name
from ..const import LOGGER


def debug_enabled(entry) -> bool:
    from ..const import CONF_DEBUG

    return bool(entry.options.get(CONF_DEBUG, False))


def log_debug(entry, msg: str, *args) -> None:
    if debug_enabled(entry):
        LOGGER.debug(msg, *args)
