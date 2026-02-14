"""
ログレベル設定ガイド

このファイルは、3 種類に分類されたログレベル設定の使用方法を説明します。
"""

# ========================================
# ログレベル設定の概要
# ========================================

# 本アプリケーションのログは、以下の 3 種類に分離されており、
# 環境変数で独立して制御できます：

# 1. APP_LOG_LEVEL
#    - アプリケーション・Azure SDK・Microsoft Graph SDK のログをまとめて制御
#    - 対象ロガー:
#      * アプリケーションコード (main, tools, common など)
#      * Azure SDK (azure.*)
#      * Microsoft Graph SDK (msgraph, kiota)
#      * HTTP ライブラリ (urllib3, httpx, httpcore)
#    - 既定値: INFO
#    - 環境変数: APP_LOG_LEVEL

# 2. AUTH_LOG_LEVEL
#    - Entra 認証・MSAL のログを制御
#    - 対象ロガー:
#      * auth.entra_auth_provider
#      * auth.obo_client
#      * auth.claims_helpers
#      * msal
#    - 既定値: APP_LOG_LEVEL と同じ値
#    - 環境変数: AUTH_LOG_LEVEL

# 3. MCP_SERVER_LOG_LEVEL
#    - FastMCP サーバーと関連ライブラリのログを制御
#    - 対象ロガー:
#      * fastmcp
#      * starlette
#      * MCP サーバー依存ライブラリ:
#        - fakeredis
#        - docket、docker
#        - mcp.server.lowlevel.server
#        - mcp.server.streamable_http
#        - sse_starlette.sse
#    - 既定値: APP_LOG_LEVEL と同じ値
#    - 環境変数: MCP_SERVER_LOG_LEVEL

# ========================================
# 使用例
# ========================================

# # すべてのログを INFO レベル（既定）で実行
# export APP_LOG_LEVEL=INFO
# export AUTH_LOG_LEVEL=INFO  # 未指定なら APP_LOG_LEVEL と同じ
# export MCP_SERVER_LOG_LEVEL=INFO  # 未指定なら APP_LOG_LEVEL と同じ
# python src/main.py


# # アプリのログは INFO、認証は DEBUG、MCP サーバーは WARNING で実行
# export APP_LOG_LEVEL=INFO
# export AUTH_LOG_LEVEL=DEBUG
# export MCP_SERVER_LOG_LEVEL=WARNING
# python src/main.py


# # 全体を DEBUG にして詳細デバッグ
# export APP_LOG_LEVEL=DEBUG
# python src/main.py


# # アプリは INFO、認証だけ DEBUG で詳細に、MCP サーバーは ERROR のみ
# export APP_LOG_LEVEL=INFO
# export AUTH_LOG_LEVEL=DEBUG
# export MCP_SERVER_LOG_LEVEL=ERROR
# python src/main.py


# # Azure SDK / Graph SDK のデバッグログを詳細に見たい場合
# export APP_LOG_LEVEL=DEBUG
# export AUTH_LOG_LEVEL=INFO
# export MCP_SERVER_LOG_LEVEL=INFO
# python src/main.py
# → Azure SDK、Microsoft Graph SDK、HTTP ライブラリのデバッグログが表示される


# # MCP サーバー関連のデバッグログのみを見たい場合
# export APP_LOG_LEVEL=INFO
# export AUTH_LOG_LEVEL=INFO
# export MCP_SERVER_LOG_LEVEL=DEBUG
# python src/main.py
# → FastMCP、Starlette、fakeredis、docket などのデバッグログが表示される

# ========================================
# ログレベルの説明
# ========================================

# CRITICAL: 重大なエラー（プログラムが続行不可）
# ERROR:    エラー（機能の一部が動作しない）
# WARNING:  警告（注意が必要）
# INFO:     情報（動作経過の情報）
# DEBUG:    デバッグ情報（開発時のトレース）

# ========================================
# ロギング設定の実装詳細
# ========================================

# ロギング設定クラス: common.logging_config.LoggerConfig
#
# 設定方法：
#   - ルートロガーレベル: 3 種類のログレベルの最小値に自動設定
#     これにより、各ロガーが個別のレベルで正しくフィルタリングできます
#
#   - アプリケーションロガー:
#     main, tools.*, common.*、azure.*、msgraph、kiota
#     → APP_LOG_LEVEL で制御
#
#   - 認証ロガー:
#     auth.*, msal
#     → AUTH_LOG_LEVEL で制御
#
#   - MCP サーバージロガー:
#     fastmcp、starlette、fakeredis、docket、docker など
#     → MCP_SERVER_LOG_LEVEL で制御
#
# 初期化時に LoggerConfig.configure() を呼び出して、
# すべてのロガーに設定を適用します。

# ========================================
# 環境変数の .env ファイルでの設定
# ========================================

# .env ファイルに以下のように記述できます：

# # アプリケーション設定
# APP_LOG_LEVEL=INFO
# AUTH_LOG_LEVEL=DEBUG
# MCP_SERVER_LOG_LEVEL=WARNING

# # Entra ID 設定
# ENTRA_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# ENTRA_APP_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# ENTRA_APP_CLIENT_SECRET=your-secret-here
# ENTRA_REQUIRED_SCOPES=https://graph.microsoft.com/.default

# # MCP サーバー設定
# MCP_TRANSPORT=streamable-http
# MCP_HOST=0.0.0.0
# MCP_PORT=8000

# ========================================
# トラブルシューティング
# ========================================

# Q. APP_LOG_LEVEL=DEBUG にしても Graph SDK のログが出ない
# A. ルートロガーレベルが自動計算されます。MCP_SERVER_LOG_LEVEL が高い場合、
#    MCP_SERVER_LOG_LEVEL も DEBUG に設定してください。
#
#    export APP_LOG_LEVEL=DEBUG
#    export MCP_SERVER_LOG_LEVEL=DEBUG

# Q. MCP サーバーのログだけを見たい
# A. MCP_SERVER_LOG_LEVEL に DEBUG、APP_LOG_LEVEL に INFO を設定してください：
#
#    export APP_LOG_LEVEL=INFO
#    export AUTH_LOG_LEVEL=INFO
#    export MCP_SERVER_LOG_LEVEL=DEBUG

# Q. 認証周辺のログだけが欲しい場合
# A. AUTH_LOG_LEVEL を DEBUG に設定してください：
#
#    export APP_LOG_LEVEL=INFO
#    export AUTH_LOG_LEVEL=DEBUG
#    export MCP_SERVER_LOG_LEVEL=INFO

```