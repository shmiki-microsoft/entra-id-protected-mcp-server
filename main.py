"""
Entra ID 認証で保護された FastMCP サーバーのエントリーポイント。

このサーバーは、Microsoft Entra ID (旧 Azure AD) のトークンを検証する
`EntraIDAuthProvider` を通して保護されます。必要な環境変数:

- ENTRA_TENANT_ID: テナント ID (GUID)
- ENTRA_AUDIENCE: 受信者 (API / クライアント ID)
- ENTRA_REQUIRED_SCOPES: 要求するスコープ (カンマ区切り、任意)

提供するツール `get_user_info` は、認証済みユーザーのトークンから
主要なクレーム情報を返します。
"""
import logging
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from auth.entra_auth_provider import EntraIDAuthProvider
from config import Settings
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

# ===== Tool =====
@mcp.tool()
async def get_user_info():
    """認証済みの Azure (Entra ID) ユーザー情報を返します。

    現在リクエストのコンテキストにあるアクセストークンからクレームを取得し、
    主な識別子・プロフィール・ロール・スコープなどをまとめて返します。
    """
    # FastMCP 依存性から現在のアクセストークンを取得
    token = get_access_token()
    # JWT のクレーム (tid, sub, upn など) を参照
    claims = token.claims
    logger.debug(
        "get_user_info invoked: tenant_id=%s subject=%s client_id=%s",
        claims.get("tid"),
        claims.get("sub"),
        token.client_id,
    )
    # 代表的なクレームをそのまま返却 (存在しない場合は None)
    return {
        "subject": claims.get("sub"),
        "client_id": token.client_id,
        "tenant_id": claims.get("tid"),
        "issuer": claims.get("iss"),
        "object_id": claims.get("oid"),
        "user_principal_name": claims.get("upn"),
        "email": claims.get("email") or claims.get("preferred_username"),
        "name": claims.get("name"),
        "given_name": claims.get("given_name"),
        "family_name": claims.get("family_name"),
        "job_title": claims.get("job_title"),
        "department": claims.get("department"),
        "office_location": claims.get("office_location"),
        "scopes": token.scopes,
        "roles": claims.get("roles", []),
        "amr": claims.get("amr"),
        "auth_methods": claims.get("amr"),
        "issued_at": claims.get("iat"),
        "expires_at": claims.get("exp"),
        "not_before": claims.get("nbf"),
        "app_id": claims.get("appid"),
        "azp": claims.get("azp"),
        "idp": claims.get("idp"),
        "ver": claims.get("ver"),
    }

if __name__ == "__main__":
    # HTTP トランスポートで起動。localhost:8000 で待機します。
    mcp.run(
        transport=settings.mcp_transport,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=APP_LOG_LEVEL,
    )
