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
        そのクレームの値を返します。
        """
        roles, user_id, client_id, scopes, claims = get_user_context()

        logger.debug(
            "get_user_info invoked: tenant_id=%s subject=%s client_id=%s roles=%s scopes=%s",
            claims.get("tid"),
            user_id,
            client_id,
            roles,
            scopes,
        )

        return claims
