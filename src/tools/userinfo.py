"""ユーザー情報関連の MCP ツール群。"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from auth.claims_helpers import get_user_context

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """ユーザー情報系ツールを FastMCP に登録する。"""

    @mcp.tool()
    async def get_user_info():
        """認証済みの Azure (Entra ID) ユーザー情報を返します。

        現在リクエストのコンテキストにあるアクセストークンからクレームを取得し、
        主な識別子・プロフィール・ロール・スコープなどをまとめて返します。
        """
        # 現在のアクセストークンとユーザーコンテキストを取得
        roles, user_id, client_id, scopes, claims = get_user_context()

        logger.debug(
            "get_user_info invoked: tenant_id=%s subject=%s client_id=%s roles=%s scopes=%s",
            claims.get("tid"),
            user_id,
            client_id,
            roles,
            scopes,
        )
        # 代表的なクレームをそのまま返却 (存在しない場合は None)
        return {
            "subject": user_id,
            "client_id": client_id,
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
            "scopes": scopes,
            "roles": roles,
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
