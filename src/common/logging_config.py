"""
ロギング設定を一元管理するモジュール。

3 種類のログレベルを環境変数で個別制御できます：
- APP_LOG_LEVEL: アプリ・Azure SDK・Microsoft Graph SDK のログレベル（統一）
- AUTH_LOG_LEVEL: Entra 認証・MSAL のログレベル
- MCP_SERVER_LOG_LEVEL: MCP サーバーのログレベル（分離）

すべてのロガー設定はこのモジュールで一元管理されます。
"""

import logging
from typing import Optional


class LoggerConfig:
    """ロギング設定を管理するクラス。"""

    # ロガー名のマッピング定義
    LOGGER_GROUPS = {
        "app": [
            # アプリケーション関連
            "main",
            "tools",
            "tools.azure_vm",
            "tools.graph_user",
            "tools.role_based_info",
            "tools.userinfo",
            "common",
            "common.config",
            "common.utils",
        ],
        "auth": [
            # 認証関連（Entra ID・MSAL）
            "auth",
            "auth.entra_auth_provider",
            "auth.obo_client",
            "auth.claims_helpers",
            "msal",
        ],
        "azure": [
            # Azure SDK・Microsoft Graph SDK
            "azure",
            "msgraph",
            "kiota",
        ],
        "mcp_server": [
            # MCP サーバー関連
            "fastmcp",
            "starlette",
        ],
    }

    def __init__(
        self,
        app_log_level: Optional[str] = None,
        auth_log_level: Optional[str] = None,
        mcp_server_log_level: Optional[str] = None,
        format_string: Optional[str] = None,
    ):
        """ロギング設定を初期化する。

        Args:
            app_log_level: アプリログレベル（未指定なら INFO）
            auth_log_level: 認証ログレベル（未指定なら app_log_level と同じ）
            mcp_server_log_level: MCP サーバーログレベル（未指定なら app_log_level と同じ）
            format_string: ログフォーマット（未指定なら標準フォーマット）
        """
        self.app_log_level = (app_log_level or "INFO").upper()
        self.auth_log_level = (auth_log_level or self.app_log_level).upper()
        self.mcp_server_log_level = (mcp_server_log_level or self.app_log_level).upper()

        self.format_string = (
            format_string or "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )

    def configure(self) -> None:
        """全ロガーの設定を適用する。"""
        # ルートロガーのレベルを全てのログレベルの最小値（最も詳細）に設定
        # これにより、各ロガーが自身のレベルでフィルタリングできる
        all_levels = [
            getattr(logging, self.app_log_level),
            getattr(logging, self.auth_log_level),
            getattr(logging, self.mcp_server_log_level),
        ]
        root_level = min(all_levels)

        logging.basicConfig(
            level=root_level,
            format=self.format_string,
        )

        # 各グループのロガーに個別レベルを適用
        for logger_name in self.LOGGER_GROUPS["app"]:
            logging.getLogger(logger_name).setLevel(self.app_log_level)

        for logger_name in self.LOGGER_GROUPS["auth"]:
            logging.getLogger(logger_name).setLevel(self.auth_log_level)

        for logger_name in self.LOGGER_GROUPS["azure"]:
            logging.getLogger(logger_name).setLevel(self.app_log_level)

        for logger_name in self.LOGGER_GROUPS["mcp_server"]:
            logging.getLogger(logger_name).setLevel(self.mcp_server_log_level)

        # ルートロガー以外のサードパーティライブラリは MCP_SERVER_LOG_LEVEL で制御
        # 既知のロガーをリストアップして明示的に制御
        third_party_loggers = [
            "fakeredis",
            "docket",
            "docker",
            "mcp.server.lowlevel.server",
            "mcp.server.streamable_http",
            "sse_starlette.sse",
        ]
        for logger_name in third_party_loggers:
            logging.getLogger(logger_name).setLevel(self.mcp_server_log_level)

    def get_app_logger(self, name: str) -> logging.Logger:
        """アプリロガーを取得する。"""
        logger = logging.getLogger(name)
        logger.setLevel(self.app_log_level)
        return logger

    def get_auth_logger(self, name: str) -> logging.Logger:
        """認証ロガーを取得する。"""
        logger = logging.getLogger(name)
        logger.setLevel(self.auth_log_level)
        return logger

    def get_mcp_server_logger(self, name: str) -> logging.Logger:
        """MCP サーバーロガーを取得する。"""
        logger = logging.getLogger(name)
        logger.setLevel(self.mcp_server_log_level)
        return logger

    def __str__(self) -> str:
        """設定内容を文字列で返す。"""
        return (
            f"LoggerConfig(app={self.app_log_level}, "
            f"auth={self.auth_log_level}, "
            f"mcp_server={self.mcp_server_log_level})"
        )
