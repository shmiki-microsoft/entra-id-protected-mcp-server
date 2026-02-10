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

`.env` に設定する主な値:

```dotenv
ENTRA_TENANT_ID=your-tenant-id-here          # テナント ID (GUID)
ENTRA_AUDIENCE=your-client-or-api-id-here    # アプリ / API のクライアント ID
ENTRA_REQUIRED_SCOPES=access_as_user         # 要求スコープ（カンマ区切りで複数指定可）
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

## ライセンス

ライセンス情報が必要な場合は、プロジェクトポリシーに従って `LICENSE` ファイルを追加してください。