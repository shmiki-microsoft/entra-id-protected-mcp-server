"""ユーザー情報関連の MCP ツール群。"""
from __future__ import annotations

import logging
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """ユーザー情報系ツールを FastMCP に登録する。"""

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
