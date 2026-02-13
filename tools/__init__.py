"""MCP ツールパッケージ。

`tools` 配下の各モジュールが `register_tools(mcp)` 関数を実装している場合、
`register_all_tools` 呼び出し時に自動的に登録されます。
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_all_tools(mcp: FastMCP) -> None:
    """tools パッケージ配下のツールを一括登録する。

    新しいツールを追加したい場合は、tools/ 配下にモジュールを追加し、
    その中で `register_tools(mcp)` 関数を定義してください。
    """
    for module_info in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        module_name = f"{__name__}.{module_info.name}"
        module = importlib.import_module(module_name)
        register = getattr(module, "register_tools", None)
        if callable(register):  # type: ignore[arg-type]
            logger.debug("Registering tools from %s", module_name)
            register(mcp)  # type: ignore[misc]
