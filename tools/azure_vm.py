"""Azure Virtual Machines 一覧取得用 MCP ツール。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from azure.mgmt.compute import ComputeManagementClient
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from auth.obo_client import OboSettings, OnBehalfOfCredential
from config import Settings

logger = logging.getLogger(__name__)

_settings = Settings()


def _build_obo_credential(user_jwt: str) -> OnBehalfOfCredential:
    """現在のユーザー トークンを元に OBO 用の Credential を構築する。"""
    if not _settings.entra_tenant_id:
        raise RuntimeError("ENTRA_TENANT_ID is not configured")
    if not _settings.entra_app_client_id or not _settings.entra_app_client_secret:
        raise RuntimeError("ENTRA_APP_CLIENT_ID / ENTRA_APP_CLIENT_SECRET are not configured")

    obo_settings = OboSettings(
        tenant_id=_settings.entra_tenant_id,
        client_id=_settings.entra_app_client_id,
        client_secret=_settings.entra_app_client_secret,
        scope=_settings.azure_obo_scope,
    )
    return OnBehalfOfCredential(obo_settings, user_jwt)


def register_tools(mcp: FastMCP) -> None:
    """Azure VM 関連ツールを FastMCP に登録する。"""

    @mcp.tool()
    async def list_azure_vms(subscription_id: str) -> List[Dict[str, Any]]:
        """指定したサブスクリプション内の Azure VM 一覧を取得します。

        認証済みユーザーのアクセストークンを On-Behalf-Of フローで交換し、
        Azure Resource Manager (`https://management.azure.com/`) に対して
        Azure SDK (azure-mgmt-compute) を用いて VM 一覧を取得します。

        引数:
            subscription_id: VM を列挙する対象のサブスクリプション ID。
        """

        # FastMCP から現在のユーザー アクセストークンを取得
        access_token = get_access_token()
        credential = _build_obo_credential(access_token.token)

        # AZURE_SDK_LOG_LEVEL が DEBUG の場合のみ、HTTP ログを詳細に出す
        azure_sdk_level = (
            _settings.azure_sdk_log_level or _settings.mcp_log_level or "INFO"
        ).upper()

        if azure_sdk_level == "DEBUG":
            client = ComputeManagementClient(
                credential,
                subscription_id,
                logging_body=True,
                logging_enable=True,
            )
        else:
            client = ComputeManagementClient(credential, subscription_id)

        vms: List[Dict[str, Any]] = []
        for vm in client.virtual_machines.list_all():
            vms.append(
                {
                    "id": vm.id,
                    "name": vm.name,
                    "location": vm.location,
                    "type": vm.type,
                    "tags": vm.tags,
                }
            )

        logger.info("Fetched %d VMs from subscription %s", len(vms), subscription_id)
        return vms
