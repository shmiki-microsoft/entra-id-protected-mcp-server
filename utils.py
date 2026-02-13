"""
ユーティリティ関数群。
"""
import json
from typing import Any, Dict, List

from kiota_serialization_json.json_serialization_writer import (
    JsonSerializationWriter,
)


def parse_scopes(raw: str) -> List[str]:
    """カンマ区切りスコープ文字列を正規化して一覧化。

    - 前後空白除去
    - 空要素除去
    - 小文字化
    - 重複除去
    - ソート
    """
    items = {s.strip().lower() for s in (raw or "").split(",") if s.strip()}
    return sorted(items)


def graph_serialize_model(model: Any) -> Dict[str, Any]:
    """Microsoft Graph の Kiota モデルを JSON(dict) に変換する。"""
    writer = JsonSerializationWriter()
    writer.write_object_value(None, model)
    json_bytes = writer.get_serialized_content()
    return json.loads(json_bytes.decode("utf-8"))
