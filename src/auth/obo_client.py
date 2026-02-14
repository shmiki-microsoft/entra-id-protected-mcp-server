"""Microsoft Entra ID のアクセストークンを使った
On-Behalf-Of (OBO) フロー実装モジュール。

MSAL を用いて、クライアント資格情報 + ユーザーのアクセストークンを元に
Azure リソース管理用のアクセストークンを取得します。
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import msal
from azure.core.credentials import AccessToken, TokenCredential

logger = logging.getLogger(__name__)


@dataclass
class OboSettings:
    """OBO フローに必要な設定値。"""

    tenant_id: str
    client_id: str
    client_secret: str
    scope: str  # 例: "https://management.azure.com/.default"


class OnBehalfOfCredential(TokenCredential):
    """MSAL ベースの On-Behalf-Of フローを行う TokenCredential 実装。"""

    def __init__(self, settings: OboSettings, user_assertion: str) -> None:
        self._settings = settings
        self._user_assertion = user_assertion

    def get_token(self, *scopes: str, **kwargs) -> AccessToken:  # type: ignore[override]
        """Azure SDK から要求されたスコープに関わらず、settings.scope でトークンを取得。"""
        authority = f"https://login.microsoftonline.com/{self._settings.tenant_id}"
        logger.debug(
            "Starting OBO token acquisition: tenant_id=%s client_id=%s scope=%s",
            self._settings.tenant_id,
            self._settings.client_id,
            self._settings.scope,
        )
        app = msal.ConfidentialClientApplication(
            client_id=self._settings.client_id,
            client_credential=self._settings.client_secret,
            authority=authority,
        )

        result = app.acquire_token_on_behalf_of(
            user_assertion=self._user_assertion,
            scopes=[self._settings.scope],
        )

        if "access_token" not in result:
            error = result.get("error_description") or result.get("error") or "unknown_error"
            logger.error("Failed to acquire OBO token: %s", error)
            raise RuntimeError(f"obo_token_acquisition_failed: {error}")

        expires_in = int(result.get("expires_in", 3599))
        expires_on = int(time.time()) + expires_in
        logger.debug("OBO access token acquired; expires_in=%s", expires_in)
        return AccessToken(result["access_token"], expires_on)
