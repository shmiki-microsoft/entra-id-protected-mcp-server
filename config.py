"""
環境変数を集中管理する設定モジュール。

`.env` を読み込んだ上で、Entra ID 関連とログ・起動設定を提供します。
"""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    """環境変数から Entra ID とログ・MCP 起動設定を
    読み込んで提供する設定クラス。"""
    # Entra ID
    entra_tenant_id: str = os.getenv("ENTRA_TENANT_ID", "")
    entra_audience: str = os.getenv("ENTRA_AUDIENCE", "")
    entra_required_scopes_raw: str = os.getenv("ENTRA_REQUIRED_SCOPES", "")

    # ログ
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # MCP 起動設定
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp_host: str = os.getenv("MCP_HOST", "localhost")
    mcp_port: int = int(os.getenv("MCP_PORT", "8000"))
