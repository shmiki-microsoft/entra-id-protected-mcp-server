# Entra ID Protected MCP Server

Microsoft Entra ID (旧 Azure AD) のアクセストークン検証で保護された FastMCP サーバーです。

認証済みユーザーのトークンからクレーム情報を取得する `get_user_info` ツールを 1 つ提供し、
MCP クライアント（例: MCP 対応のエージェント / エディタ拡張）から安全にユーザー情報へアクセスできるようにします。

---

## 機能概要

- Microsoft Entra ID のアクセストークン (JWT) を検証
  - 署名検証 (JWKS)
  - `aud` / `iss` 検証
  - 必須スコープ検証 (`ENTRA_REQUIRED_SCOPES`)
- FastMCP ベースの MCP サーバーとして起動
  - デフォルトでは `streamable-http` トランスポートで `localhost:8000` で待ち受け
- MCP ツール `get_user_info`
  - 認証済みユーザーのクレームをまとめて返す
  - 代表的な項目: `subject`, `tenant_id`, `user_principal_name`, `email`, `name`, `roles`, `scopes` など

---

## ディレクトリ構成

- `main.py`
  - エントリーポイント。`Settings` と `EntraIDAuthProvider` を使って FastMCP サーバーを起動
  - MCP ツール `get_user_info` の実装
- `config.py`
  - 環境変数を読み込む設定クラス `Settings`
- `utils.py`
  - スコープ文字列を整形する `parse_scopes`
- `auth/entra_auth_provider.py`
  - Microsoft Entra ID のトークン検証を行う `EntraIDAuthProvider`
- `.env.example`
  - 必要な環境変数のサンプル
- `requirements.txt`
  - 依存パッケージ定義

---

## 必要要件

- Python 3.11 以降を推奨
- Microsoft Entra ID (旧 Azure AD) テナント
  - API 用クライアント/アプリケーション登録
  - アクセストークンを発行できる環境（例: SPA / Web アプリ / CLI など）

---

## Microsoft Entra ID のアプリ登録とスコープ作成

この MCP サーバーは、Microsoft Entra ID の v2.0 アクセストークン (アプリ マニフェストの `requestedAccessTokenVersion=2`) を前提としています。
そのため、まず Microsoft Entra ID に API 用アプリ登録とスコープ定義を行い、あわせてマニフェストでアクセストークン バージョンを 2 に設定します。

1. Azure ポータルでアプリ登録
  - Azure ポータル → 「Microsoft Entra ID」→「アプリの登録」→「新規登録」
  - 任意の名前を設定し、「登録」をクリック
  - 登録後に表示される次の値を控えておきます:
    - 「ディレクトリ (テナント) ID」 → `.env` の `ENTRA_TENANT_ID` に転記
    - 「アプリケーション (クライアント) ID」

2. アプリ マニフェストで `requestedAccessTokenVersion` を 2 に設定
  - 対象アプリの「マニフェスト」メニューを開く
  - `requestedAccessTokenVersion` プロパティを `2` に設定し、保存
  - これにより、このアプリから発行されるアクセストークンは v2.0 形式になります

3. アプリケーション ID URI の設定 (Expose an API)
  - 対象アプリの「Expose an API (API の公開)」に移動
  - 「Set」または「Application ID URI の設定」から、アプリケーション ID URI を設定
    - 例: `api://<アプリケーションID>` あるいは独自の URI
  - 設定した値を `.env` の `ENTRA_AUDIENCE` および Azure CLI 例の `$RESOURCE` に使用します。

4. スコープ (`access_as_user`) の作成
  - 同じく「Expose an API (API の公開)」→「Add a scope (スコープの追加)」
  - Scope name に `access_as_user` を指定
  - Who can consent は「Admins and users」など適切なものを選択
  - Display name / Description / Admin consent display name などを入力し、「Enabled」がオンであることを確認して保存
  - このスコープ名は `.env` の `ENTRA_REQUIRED_SCOPES` と一致させます (例: `ENTRA_REQUIRED_SCOPES=access_as_user`)。

5. クライアントアプリからの利用
  - フロントエンドや CLI アプリ側で、上記アプリケーション ID URI とスコープ (`access_as_user`) を指定してアクセストークンを取得します。
  - 例: Azure CLI からは、`$RESOURCE` をアプリケーション ID URI に設定し、`$RESOURCE/access_as_user` でログイン・トークン要求を行います。

これにより、MCP サーバー側では `ENTRA_TENANT_ID` / `ENTRA_AUDIENCE` / `ENTRA_REQUIRED_SCOPES` を使ってトークン検証を行い、`get_user_info` ツールからクレームを参照できるようになります。

---

## セットアップ

1. リポジトリのクローン

```bash
git clone <this-repo-url>
cd entra-id-protected-mcp-server
```

2. 仮想環境の作成と有効化 (任意)

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
```

3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

4. 環境変数の設定

`.env.example` を `.env` にコピーし、自分の環境に合わせて値を変更します。

```bash
copy .env.example .env  # Windows
```

上記の「Microsoft Entra ID のアプリ登録とスコープ作成」で取得・設定した値を `.env` に転記します。

`.env` に設定する主な値:

```dotenv
ENTRA_TENANT_ID=your-tenant-id-here          # テナント ID (GUID) - アプリ登録の「ディレクトリ (テナント) ID」
ENTRA_AUDIENCE=your-client-or-api-id-here    # アプリ の クライアント ID
ENTRA_REQUIRED_SCOPES=access_as_user         # 要求スコープ（カンマ区切りで複数指定可）- 作成したスコープ名
LOG_LEVEL=INFO                               # ログレベル (DEBUG/INFO/WARN/ERROR)
MCP_TRANSPORT=streamable-http                # トランスポート種別
MCP_HOST=localhost                           # バインドするホスト
MCP_PORT=8000                                # 待受ポート
```

> ※ `.env` の読み込みは FastMCP / 実行環境側で行ってください。VS Code や MCP ランタイムで `.env` を読み込む設定が必要な場合があります。

---
## 実行方法

ローカルで MCP サーバーを HTTP 経由で起動する場合:

```bash
python main.py
```

デフォルトでは以下で待ち受けます:

- ホスト: `localhost`
- ポート: `8000`
- トランスポート: `streamable-http`

ログには、読み込んだテナント ID や Audience、スコープ設定が INFO レベルで出力されます。

---

## アクセストークン取得例 (Azure CLI)

MCP サーバーに渡す Microsoft Entra ID のアクセストークンは、例として Azure CLI から次のように取得できます。

```pwsh
$RESOURCE = "Entra ID に登録したアプリの アプリケーション ID URI を指定"
# 例) $RESOURCE = "api://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

az login --scope "$RESOURCE/access_as_user"
az account get-access-token --resource $RESOURCE --query accessToken -o tsv
```

- 上記では `access_as_user` スコープを要求しています（`.env` の `ENTRA_REQUIRED_SCOPES` と合わせてください）。
- 取得したトークン文字列を、MCP クライアント側で HTTP ヘッダー `Authorization: Bearer <access_token>` に設定してこのサーバーに送信します。

---

## VS Code でのデバッグ実行

このリポジトリには VS Code 用のデバッグ構成が含まれています（`.vscode/launch.json`）。

1. 事前準備
  - `.env` を作成し、必要な値を設定しておきます
  - `pip install -r requirements.txt` 済みであること
2. VS Code でこのフォルダーを開く
3. 実行とデバッグビューで「Run MCP Server」を選択
4. F5 または「デバッグの開始」で起動

`Run MCP Server` 構成は次のような設定になっており、`.env` を自動で読み込みつつ `main.py` を起動します。

- `program`: `main.py`
- `envFile`: `${workspaceFolder}/.env`
- コンソール: 統合ターミナル

ブレークポイントを `main.py` や `auth/entra_auth_provider.py` に設定しておくことで、トークン検証やツール実行の挙動をステップ実行で確認できます。

---

## MCP Inspector でのテスト

このプロジェクトには MCP Inspector を使ったテスト用の VS Code 構成も含まれています。

### 前提条件

- Node.js（推奨: v18 以降）がインストールされていること
- MCP サーバーが起動済みであること
  - 例: 上記「Run MCP Server」構成で `localhost:8000` で待ち受け

### 起動手順

1. VS Code の実行とデバッグビューで「Run MCP Inspector」を選択
2. F5 または「デバッグの開始」で起動
3. ブラウザで MCP Inspector が開くので、画面の指示に従って MCP サーバーを追加します
  - トランスポート: HTTP / `streamable-http`
  - URL: `http://localhost:8000/mcp`（必要に応じてホスト・ポートを `.env` に合わせて変更）
  - Authentication: 取得したアクセストークンを HTTP ヘッダー `Authorization: Bearer <access_token>` として送信するよう設定

Inspector 上から `get_user_info` ツールを呼び出すことで、実際に発行したアクセストークンに基づいたクレーム情報を対話的に確認できます。

---

## 認証フロー概要

1. クライアント (フロントエンド / CLI / エージェントなど) が Microsoft Entra ID からアクセストークンを取得
2. そのアクセストークンを `Authorization: Bearer <token>` として MCP サーバーに送信
3. `auth/entra_auth_provider.py` の `EntraIDAuthProvider` が次を検証
   - 署名検証 (Entra の JWKS を取得して JOSE で検証)
   - `audience` が `ENTRA_AUDIENCE` と一致しているか
   - `issuer` がテナントに対応した URL か
   - 必須スコープ (`ENTRA_REQUIRED_SCOPES`) をすべて満たしているか
4. 検証成功時、FastMCP の `AccessToken` としてトークン情報をコンテキストに保存
5. MCP ツール側 (`get_user_info`) から `get_access_token()` を通じてクレームにアクセス

トークンが無効・期限切れ・スコープ不足の場合は `AuthenticationError` が投げられます。

---

## 提供ツール: `get_user_info`

`get_user_info` は、現在のリクエストで使用しているアクセストークンから代表的なクレームを抜き出して返します。

返却される主なフィールド:

- `subject` (`sub`)
- `client_id` (`azp` または `appid`)
- `tenant_id` (`tid`)
- `issuer` (`iss`)
- `object_id` (`oid`)
- `user_principal_name` (`upn`)
- `email` (`email` または `preferred_username`)
- `name`, `given_name`, `family_name`
- `job_title`, `department`, `office_location`
- `scopes` (スペース区切り `scp` を分解した配列)
- `roles` (ロールクレーム)
- `issued_at` (`iat`), `expires_at` (`exp`), `not_before` (`nbf`)
- そのほか `app_id`, `azp`, `idp`, `ver` など

これにより、MCP クライアントは「誰が」「どの権限で」アクセスしているかを簡単に把握できます。

---

## スコープ設定 (`ENTRA_REQUIRED_SCOPES`)

`ENTRA_REQUIRED_SCOPES` はカンマ区切りでスコープを列挙します。`utils.parse_scopes` によって次のように正規化されます。

- 前後の空白削除
- 小文字化
- 空要素の除去
- 重複削除
- ソート

例:

```dotenv
ENTRA_REQUIRED_SCOPES=access_as_user, User.Read,  files.read
```

→ 実際に検証されるスコープ一覧: `["access_as_user", "files.read", "user.read"]`

---

## エラーとログ

- JWKS 取得失敗
  - 起動時に `jwks_fetch_failed` という `ValueError` を投げ、ログに詳細を出力
- アクセストークン期限切れ
  - `access_token_expired` という `AuthenticationError`
- 不正なアクセストークン
  - `invalid_access_token` という `AuthenticationError`
- 必須スコープ不足
  - `missing_required_scopes` という `AuthenticationError`

ログレベルは `LOG_LEVEL` で制御できます (デフォルト: `INFO`)。

---

## 開発メモ

- 認証方式や返却クレームを拡張したい場合は:
  - 認証ロジック: `auth/entra_auth_provider.py`
  - 戻り値の形式: `main.py` の `get_user_info` 関数
- 追加 MCP ツールを増やしたい場合は:
  - `main.py` 内で `@mcp.tool()` デコレータを付けた関数を追加してください。

---