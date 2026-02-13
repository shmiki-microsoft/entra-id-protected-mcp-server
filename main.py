"""Entra ID 認証で保護された FastMCP サーバーのエントリーポイント。

このサーバーは、Microsoft Entra ID (旧 Azure AD) のトークンを検証する
`EntraIDAuthProvider` を通して保護されます。必要な環境変数:

- ENTRA_TENANT_ID: テナント ID (GUID)
- ENTRA_AUDIENCE: 受信者 (API / クライアント ID)
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
APP_LOG_LEVEL = (settings.log_level or "INFO").upper()

# Entra 認証プロバイダ用のログレベル (未指定ならアプリと同じ)
ENTRA_AUTH_LOG_LEVEL = (
    settings.entra_auth_log_level or settings.log_level or "INFO"
).upper()

logging.basicConfig(
    level=APP_LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 認証プロバイダのロガーに専用レベルを適用
logging.getLogger("auth.entra_auth_provider").setLevel(ENTRA_AUTH_LOG_LEVEL)

# Entra ID 設定 (必須)。`.env` または環境変数から読み込みます。
tenant_id = settings.entra_tenant_id
audience = settings.entra_audience
required_scopes_raw = settings.entra_required_scopes_raw

logger.info("Entra Tenant ID: %s", tenant_id)
logger.info("Entra Audience: %s", audience)
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
    audience=audience,
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
        log_level=APP_LOG_LEVEL,
    )
