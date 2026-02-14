"""Azure Virtual Machines 一覧取得用 MCP ツール。"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from azure.mgmt.compute import ComputeManagementClient
from fastmcp import FastMCP

from auth.claims_helpers import get_access_token_and_context
from auth.entra_auth_provider import build_obo_credential

logger = logging.getLogger(__name__)


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

        # 現在のユーザーアクセストークンとコンテキストを取得
        access_token, roles, user_id, client_id, scopes, _ = (
            get_access_token_and_context()
        )

        logger.debug(
            "list_azure_vms invoked: subscription=%s user=%s client=%s roles=%s scopes=%s",
            subscription_id,
            user_id,
            client_id,
            roles,
            scopes,
        )

        credential = build_obo_credential(
            access_token.token, "https://management.azure.com/.default"
        )

        # Azure SDK ロガーが DEBUG レベルの場合のみ、HTTP ログを詳細に出す
        azure_logger = logging.getLogger("azure")
        enable_logging = azure_logger.isEnabledFor(logging.DEBUG)

        if enable_logging:
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

        logger.info(
            "Fetched %d VMs from subscription %s for user %s",
            len(vms),
            subscription_id,
            user_id,
        )
        return vms
