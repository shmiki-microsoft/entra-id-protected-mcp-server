"""
Microsoft Entra ID (旧 Azure AD) のトークンを検証する FastMCP 用認証プロバイダ。

このモジュールは、受け取った Bearer トークン (JWT) を Entra ID の公開鍵
(JWKS) を用いて検証し、必要スコープの満たし合わせを行った上で、
FastMCP が扱える `AccessToken` オブジェクトとして返却します。
"""
import logging
import requests
from jose import jwt, JWTError, ExpiredSignatureError

from fastmcp.server.auth import AuthProvider
from fastmcp.server.auth.auth import AccessToken

logger = logging.getLogger(__name__)

class EntraIDAuthProvider(AuthProvider):
    """Entra ID ベースのトークン検証を行う認証プロバイダ。

    :param tenant_id: Entra テナント ID (GUID)
    :param audience: トークンの受信者 (API/クライアント ID)。`aud`/`azp` と整合
    :param required_scopes: 要求するスコープ一覧 (`scp` に含まれる必要あり)
    """
    def __init__(
        self,
        tenant_id: str,
        audience: str,
        required_scopes: list[str] | None = None,
        *,
        jwks_timeout: float = 5.0,
        jwks_max_retries: int = 3,
        jwks_refresh_interval_seconds: int = 3600,
    ):
        super().__init__()
        self.tenant_id = tenant_id
        self.audience = audience
        self.required_scopes = required_scopes or []
        self.jwks_timeout = jwks_timeout
        self.jwks_max_retries = jwks_max_retries
        self.jwks_refresh_interval_seconds = jwks_refresh_interval_seconds

        # FastMCP が要求する属性 (ベース URL は Entra の認証エンドポイント)
        self.base_url = "https://login.microsoftonline.com"

        # トークンの発行者 (issuer) と JWKS の取得元をテナントに合わせて設定
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.jwks_url = (
            f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        )
        logger.debug(
            "AuthProvider init: issuer=%s jwks_url=%s",
            self.issuer,
            self.jwks_url,
        )
        # 公開鍵セット (JWKS) を事前取得し、検証に利用
        # JWKS の取得はタイムアウトを設定し、失敗時はわかりやすく例外化
        try:
            response = requests.get(self.jwks_url, timeout=5)
            response.raise_for_status()
            self._jwks = response.json()
            logger.info("JWKS fetched: keys=%d", len(self._jwks.get("keys", [])))
        except requests.RequestException as exc:
            logger.error("JWKS fetch failed: %s", str(exc))
            raise ValueError("jwks_fetch_failed") from exc

    async def verify_token(self, token: str) -> AccessToken:
        """Bearer トークン (JWT) を検証し、`AccessToken` を返します。

        - 署名、`audience`、`issuer` を検証
        - `scp` (スコープ) の満たし合わせを実施 (必要な場合)
        - 問題なければ FastMCP 互換の `AccessToken` を構築
        """
        try:
            logger.debug("Verifying token: audience=%s issuer=%s", self.audience, self.issuer)
            # JOSE で JWT を検証。Entra の JWKS を用いて署名確認します。
            claims = jwt.decode(
                token,
                self._jwks,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )

            # `scp` はスペース区切りの文字列 (例: "user.read files.read")
            scopes = claims.get("scp", "").split()

            # 必須スコープが指定されている場合は、すべて含まれているか確認
            if self.required_scopes:
                required = set(self.required_scopes)
                present = set(scopes)
                if not required.issubset(present):
                    missing = list(required - present)
                    logger.warning("Missing required scopes: %s", ", ".join(missing))
                    raise JWTError("Missing required scopes")

            # FastMCP の `AccessToken` として返却 (クライアント ID は `azp`/`appid`)
            return AccessToken(
                token=token,
                claims=claims,
                scopes=scopes,
                client_id=claims.get("azp") or claims.get("appid"),
            )

        except ExpiredSignatureError as exc:
            logger.warning("Access token expired")
            raise ValueError("access_token_expired") from exc

        except JWTError as exc:
            logger.error("Invalid token: %s", str(exc))
            raise ValueError(f"invalid_token: {str(exc)}") from exc
