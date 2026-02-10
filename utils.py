"""
ユーティリティ関数群。
"""
from typing import List


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
