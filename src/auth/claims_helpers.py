"""アクセストークンのクレーム処理用ヘルパー関数群。

このモジュールは、FastMCP の依存性から取得したアクセストークンを
解析し、ユーザー情報やロール情報を抽出する汎用ヘルパーを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from fastmcp.server.dependencies import get_access_token

if TYPE_CHECKING:
    from fastmcp.server.dependencies import JWTContext


def get_user_context() -> tuple[List[str], str | None, str | None, List[str], dict]:
    """現在のアクセストークンからユーザー関連情報をまとめて取得する。

    Returns:
        tuple containing:
            - roles (List[str]): ユーザーが持つロールのリスト
            - user_id (str | None): ユーザーの subject (sub クレーム)
            - client_id (str | None): クライアント ID
            - scopes (List[str]): アクセストークンのスコープのリスト
            - claims (dict): すべてのクレームを含む辞書
    """
    access_token = get_access_token()
    claims = access_token.claims
    roles: List[str] = claims.get("roles", [])
    user_id = claims.get("sub")
    client_id = access_token.client_id
    scopes: List[str] = access_token.scopes
    return roles, user_id, client_id, scopes, claims


def get_access_token_and_context() -> tuple[
    JWTContext, List[str], str | None, str | None, List[str], dict
]:
    """アクセストークンとユーザーコンテキストを同時に取得する。

    OBO フローなどで生のトークン文字列が必要な場合に使用します。

    Returns:
        tuple containing:
            - access_token (JWTContext): アクセストークンオブジェクト
            - roles (List[str]): ユーザーが持つロールのリスト
            - user_id (str | None): ユーザーの subject (sub クレーム)
            - client_id (str | None): クライアント ID
            - scopes (List[str]): アクセストークンのスコープのリスト
            - claims (dict): すべてのクレームを含む辞書
    """
    access_token = get_access_token()
    claims = access_token.claims
    roles: List[str] = claims.get("roles", [])
    user_id = claims.get("sub")
    client_id = access_token.client_id
    scopes: List[str] = access_token.scopes
    return access_token, roles, user_id, client_id, scopes, claims


def has_role(roles: List[str], required_role: str) -> bool:
    """ユーザーが指定されたロールを持っているか確認する。

    Args:
        roles: ユーザーが持つロールのリスト
        required_role: 要求されるロール

    Returns:
        ロールを持っている場合は True
    """
    return required_role in roles
