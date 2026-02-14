# Entra ID Protected MCP Server - Test Suite

このディレクトリには、Entra ID Protected MCP Server のユニットテストが含まれています。

## 構成

```
tests/
├── __init__.py
├── conftest.py                      # pytest設定ファイル
├── test_common/                     # common モジュールのテスト
│   ├── __init__.py
│   ├── test_config.py              # 設定クラスのテスト
│   ├── test_utils.py               # ユーティリティ関数のテスト
│   └── test_logging_config.py      # ロギング設定のテスト
├── test_auth/                       # auth モジュールのテスト
│   ├── __init__.py
│   ├── test_claims_helpers.py      # クレームヘルパーのテスト
│   ├── test_obo_client.py          # OBOクライアントのテスト
│   └── test_entra_auth_provider.py # Entra認証プロバイダのテスト
└── test_tools/                      # tools モジュールのテスト
    ├── __init__.py
    ├── test_init.py                # ツール登録のテスト
    ├── test_userinfo.py            # ユーザー情報ツールのテスト
    ├── test_role_based_info.py     # ロールベース情報ツールのテスト
    ├── test_graph_user.py          # Microsoft Graph ツールのテスト
    └── test_azure_vm.py            # Azure VM ツールのテスト
```

## テストの実行方法

### すべてのテストを実行

```powershell
# プロジェクトルートで実行
python -m unittest discover -s tests -p "test_*.py" -v
```

### 特定のモジュールのテストを実行

```powershell
# common モジュールのテストのみ
python -m unittest discover -s tests/test_common -p "test_*.py" -v

# auth モジュールのテストのみ
python -m unittest discover -s tests/test_auth -p "test_*.py" -v

# tools モジュールのテストのみ
python -m unittest discover -s tests/test_tools -p "test_*.py" -v
```

### 特定のテストファイルを実行

```powershell
python -m unittest tests.test_common.test_config -v
```

### 特定のテストクラスを実行

```powershell
python -m unittest tests.test_common.test_config.TestSettings -v
```

### 特定のテストメソッドを実行

```powershell
python -m unittest tests.test_common.test_config.TestSettings.test_settings_default_values -v
```

## pytestを使用する場合

pytest をインストールしている場合は、より簡単にテストを実行できます：

```powershell
# pytestをインストール（まだの場合）
pip install pytest pytest-asyncio pytest-cov

# すべてのテストを実行
pytest tests/ -v

# カバレッジレポート付きで実行
pytest tests/ -v --cov=src --cov-report=html

# 特定のモジュールのみ
pytest tests/test_common/ -v

# 特定のテストファイル
pytest tests/test_common/test_config.py -v
```

## テストカバレッジ

各モジュールのテストは以下の内容をカバーしています：

### common モジュール

- **test_config.py**: 環境変数の読み込み、デフォルト値、型変換
- **test_utils.py**: スコープのパース、正規化、重複除去
- **test_logging_config.py**: ログレベル設定、ロガー取得、設定適用

### auth モジュール

- **test_claims_helpers.py**: クレーム抽出、ロール確認、ユーザーコンテキスト取得
- **test_obo_client.py**: OBO設定、トークン取得、エラーハンドリング
- **test_entra_auth_provider.py**: トークン検証、JWKS取得、スコープ検証、エラーハンドリング

### tools モジュール

- **test_init.py**: ツールの自動登録、モジュール検出
- **test_userinfo.py**: ユーザー情報取得ツールの登録確認
- **test_role_based_info.py**: ロールベースアクセス制御ツールの登録確認
- **test_graph_user.py**: Microsoft Graph ツールの登録確認
- **test_azure_vm.py**: Azure VM ツールの登録確認

## テストの特徴

### モッキング

外部依存関係（Microsoft Graph API、Azure SDK、MSAL など）は `unittest.mock` を使用してモック化されています。これにより：

- テストが高速に実行される
- 外部サービスへの依存がない
- 予測可能な結果が得られる

### 非同期テスト

非同期関数のテストには `async`/`await` を使用しています。

### パラメトリックテスト

複数のシナリオをテストするため、各テストメソッドで異なる入力値を使用しています。

## 注意事項

- テストは外部サービスに接続しません（すべてモック化）
- 環境変数は各テストで `patch.dict` を使用して分離されています
- FastMCP のツール実行には実際のランタイムコンテキストが必要なため、ツールの登録確認のみを行っています

## CI/CD での使用

これらのテストは CI/CD パイプラインに統合できます：

```yaml
# GitHub Actions の例
- name: Run tests
  run: |
    python -m unittest discover -s tests -p "test_*.py" -v
```

## トラブルシューティング

### ImportError が発生する場合

プロジェクトルートから実行していることを確認してください：

```powershell
cd c:\Users\mikis\Python\MCP\entra-id-protected-mcp-server
python -m unittest discover -s tests -p "test_*.py" -v
```

### ModuleNotFoundError: No module named 'src'

PYTHONPATH を設定してください：

```powershell
$env:PYTHONPATH = "c:\Users\mikis\Python\MCP\entra-id-protected-mcp-server"
python -m unittest discover -s tests -p "test_*.py" -v
```
