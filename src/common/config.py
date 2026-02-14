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
    # アプリ登録のクライアント ID (または API ID URI)
    entra_app_client_id: str = os.getenv("ENTRA_APP_CLIENT_ID", "")
    entra_required_scopes_raw: str = os.getenv("ENTRA_REQUIRED_SCOPES", "")

    # ログレベル（3 種類を個別制御可能）
    # APP_LOG_LEVEL: アプリ・Azure SDK・Microsoft Graph SDK のログレベル（統一）
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "INFO")
    # AUTH_LOG_LEVEL: Entra 認証・MSAL のログレベル（未指定なら APP_LOG_LEVEL）
    auth_log_level: str = os.getenv("AUTH_LOG_LEVEL", "")
    # MCP_SERVER_LOG_LEVEL: MCP サーバーのログレベル（未指定なら APP_LOG_LEVEL）
    mcp_server_log_level: str = os.getenv("MCP_SERVER_LOG_LEVEL", "")

    # MCP 起動設定
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp_host: str = os.getenv("MCP_HOST", "localhost")
    mcp_port: int = int(os.getenv("MCP_PORT", "8000"))

    # Azure OBO (Azure SDK から管理プレーン API を呼び出すための設定)
    # Entra アプリ (この MCP サーバー用) のクライアント シークレット
    entra_app_client_secret: str = os.getenv("ENTRA_APP_CLIENT_SECRET", "")
    # OBO で要求するスコープ。既定は管理プレーン用の .default
    azure_obo_scope: str = os.getenv(
        "AZURE_OBO_SCOPE",
        "https://management.azure.com/.default",
    )
