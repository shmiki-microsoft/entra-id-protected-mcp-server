"""Entra ID 認証で保護された FastMCP サーバーのエントリーポイント。

このサーバーは、Microsoft Entra ID (旧 Azure AD) のトークンを検証する
`EntraIDAuthProvider` を通して保護されます。必要な環境変数:

- ENTRA_TENANT_ID: テナント ID (GUID)
- ENTRA_APP_CLIENT_ID: アプリ登録のクライアント ID (または API ID URI)
- ENTRA_REQUIRED_SCOPES: 要求するスコープ (カンマ区切り、任意)

ログレベル設定:
- APP_LOG_LEVEL: アプリ・Azure SDK・Microsoft Graph SDK のログレベル（統一） (既定: INFO)
- AUTH_LOG_LEVEL: Entra 認証・MSAL のログレベル (未指定なら APP_LOG_LEVEL と同じ)
- MCP_SERVER_LOG_LEVEL: MCP サーバーのログレベル (未指定なら APP_LOG_LEVEL と同じ)

MCP ツール定義は tools パッケージ配下の各モジュールに分離されています。
"""

import logging
import warnings

from fastmcp import FastMCP

from auth.entra_auth_provider import EntraIDAuthProvider
from common.config import Settings
from common.logging_config import LoggerConfig
from common.utils import parse_scopes
from tools import register_all_tools

# kiota_abstractions と msgraph の DeprecationWarning を非表示
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="kiota_abstractions.*"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="msgraph.*")

# 設定の読み込み
settings = Settings()

# ロギング設定の初期化
logger_config = LoggerConfig(
    app_log_level=settings.app_log_level,
    auth_log_level=settings.auth_log_level or None,
    mcp_server_log_level=settings.mcp_server_log_level or None,
)
logger_config.configure()

logger = logging.getLogger(__name__)

# Entra ID 設定 (必須)。`.env` または環境変数から読み込みます。
tenant_id = settings.entra_tenant_id
app_client_id = settings.entra_app_client_id
required_scopes_raw = settings.entra_required_scopes_raw

logger.info("Logger Configuration: %s", logger_config)
logger.info("Entra Tenant ID: %s", tenant_id)

# カンマ区切りの文字列を配列へ変換し、空要素を除去
required_scopes = parse_scopes(required_scopes_raw)
logger.info(
    "Entra Required Scopes: %s",
    ", ".join(required_scopes) if required_scopes else "(none)",
)

# Entra ID ベースの認証プロバイダを初期化
auth_provider = EntraIDAuthProvider(
    tenant_id=tenant_id,
    audience=app_client_id,
    required_scopes=required_scopes,
)

# FastMCP サーバーを作成 (MCP ツール定義はこのインスタンスに紐付く)
mcp = FastMCP("entra-protected-mcp-server", auth=auth_provider)

# tools パッケージ配下のツールを一括登録
register_all_tools(mcp)

if __name__ == "__main__":
    # HTTP トランスポートで起動。localhost:8000 で待機します。
    mcp.run(
        transport=settings.mcp_transport,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=logger_config.mcp_server_log_level,
    )
