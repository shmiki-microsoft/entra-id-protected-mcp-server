"""Microsoft Graph API を使用したユーザー情報取得用 MCP ツール。

このモジュールは、Microsoft Graph SDK を用いて
https://graph.microsoft.com/v1.0/me エンドポイントをコールし、
認証済みユーザーのプロフィール情報を取得します。

On-Behalf-Of (OBO) フローを用いて、認証済みユーザーのトークンを
Microsoft Graph API 用のトークンに交換してからアクセスします。

取得した Kiota モデルは JsonSerializationWriter を用いて JSON に変換します。
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import (
    UserItemRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

from auth.entra_auth_provider import build_obo_credential
from utils import graph_serialize_model

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Microsoft Graph API 関連ツールを FastMCP に登録する。"""

    @mcp.tool()
    async def get_graph_me() -> Dict[str, Any]:
        """認証済みユーザーのプロフィール情報を取得します。"""
        try:
            access_token = get_access_token()

            logger.debug(
                "get_graph_me invoked: subject=%s client_id=%s",
                access_token.claims.get("sub"),
                access_token.client_id,
            )

            credential = build_obo_credential(
                access_token.token, "https://graph.microsoft.com/.default"
            )

            scopes = ["https://graph.microsoft.com/.default"]
            client = GraphServiceClient(credentials=credential, scopes=scopes)

            response = await client.me.get()

            data = graph_serialize_model(response)

            logger.info(
                "Successfully fetched user profile from Graph API: id=%s",
                data.get("id"),
            )

            return data

        except Exception as e:
            logger.error("Failed to fetch user profile from Graph API: %s", str(e))
            raise RuntimeError(f"graph_api_call_failed: {str(e)}") from e

    @mcp.tool()
    async def get_graph_me_with_select_query(
        select: str = "displayName,mail,id,officeLocation,jobTitle",
    ) -> Dict[str, Any]:
        """指定フィールドでユーザープロフィールを取得します。"""
        try:
            access_token = get_access_token()

            logger.debug(
                "get_graph_me_with_select_query invoked: select=%s subject=%s",
                select,
                access_token.claims.get("sub"),
            )

            credential = build_obo_credential(
                access_token.token, "https://graph.microsoft.com/.default"
            )

            scopes = ["https://graph.microsoft.com/.default"]
            client = GraphServiceClient(credentials=credential, scopes=scopes)

            select_fields = [
                field.strip() for field in select.split(",") if field.strip()
            ]

            query_params = (
                UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
                    select=select_fields,
                )
            )

            request_configuration = RequestConfiguration(
                query_parameters=query_params,
            )

            response = await client.me.get(
                request_configuration=request_configuration
            )

            data = graph_serialize_model(response)

            logger.info(
                "Successfully fetched user profile with select: id=%s fields=%s",
                data.get("id"),
                select,
            )

            return data

        except Exception as e:
            logger.error(
                "Failed to fetch user profile from Graph API with select: %s",
                str(e),
            )
            raise RuntimeError(f"graph_api_call_failed: {str(e)}") from e
