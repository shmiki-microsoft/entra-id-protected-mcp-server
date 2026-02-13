"""Entra ID 認証で保護された FastMCP サーバーのエントリーポイント。

このサーバーは、Microsoft Entra ID (旧 Azure AD) のトークンを検証する
`EntraIDAuthProvider` を通して保護されます。必要な環境変数:

- ENTRA_TENANT_ID: テナント ID (GUID)
- ENTRA_APP_CLIENT_ID: アプリ登録のクライアント ID (または API ID URI)
- ENTRA_REQUIRED_SCOPES: 要求するスコープ (カンマ区切り、任意)

MCP ツール定義は tools パッケージ配下の各モジュールに分離されています。
"""
import logging
from fastmcp import FastMCP
from auth.entra_auth_provider import EntraIDAuthProvider
from config import Settings
from tools import register_all_tools
from utils import parse_scopes

# 設定の読み込み
settings = Settings()

# アプリ(このリポジトリのコード)用のログレベル (MCP サーバーも同一レベルを使用)
MCP_LOG_LEVEL = (settings.mcp_log_level or "INFO").upper()

# Entra 認証プロバイダ用のログレベル (未指定ならアプリと同じ)
ENTRA_AUTH_LOG_LEVEL = (
    settings.entra_auth_log_level or settings.mcp_log_level or "INFO"
).upper()
# Azure SDK 用のログレベル (未指定ならアプリと同じ)
AZURE_SDK_LOG_LEVEL = (
    settings.azure_sdk_log_level or settings.mcp_log_level or "INFO"
).upper()

logging.basicConfig(
    level=MCP_LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 認証プロバイダ/ MSAL のロガーに専用レベルを適用
logging.getLogger("auth.entra_auth_provider").setLevel(ENTRA_AUTH_LOG_LEVEL)
logging.getLogger("msal").setLevel(ENTRA_AUTH_LOG_LEVEL)

# Azure SDK  ロガーに専用レベルを適用
logging.getLogger("azure").setLevel(AZURE_SDK_LOG_LEVEL)

# Entra ID 設定 (必須)。`.env` または環境変数から読み込みます。
tenant_id = settings.entra_tenant_id
app_client_id = settings.entra_app_client_id
required_scopes_raw = settings.entra_required_scopes_raw

logger.info("MCP Log Level: %s", MCP_LOG_LEVEL)
logger.info("Entra Auth Log Level: %s", ENTRA_AUTH_LOG_LEVEL)
logger.info("Azure SDK Log Level: %s", AZURE_SDK_LOG_LEVEL)
logger.info("Entra Tenant ID: %s", tenant_id)
logger.info("Entra App Client ID: %s", app_client_id)
logger.info("Entra Required Scopes(raw): %s", required_scopes_raw)

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
        log_level=MCP_LOG_LEVEL,
    )
