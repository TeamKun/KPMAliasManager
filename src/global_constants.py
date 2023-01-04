import os

ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = ""
REPO_NAME = ""
PERMISSION_LEVEL = "read"
CHECK_USER_IN_ORG = True


APPROVED_LABEL_NAME = "Status: Triage Approved"
DENIED_LABEL_NAME = "Status: Triage Denied"
PENDING_LABEL_NAME = "Status: Pending"

ALIASES_PATH = "databases.json"  # 負の遺産
ALIAS_NAME_PATTERN = r"^[a-zA-Z0-9_-]+$"

APPROVED_ISSUE_COMMENT = """
## トリアージ承認済み

### :tada: あなたのリクエスト **{alias_name}** は承認されました！ :tada:

エイリアスが追加されるまでしばらくお待ちください。

"""
DENIED_ISSUE_COMMENT = """
## トリアージ拒否 

### :no_entry_sign: あなたのリクエスト **{alias_name}** は以下の理由により拒否されました。

{reason}({raw_reason})

"""
DENY_REASONS = {
    "UNAUTHORIZED::NOT_IN_ORGANIZATION": "あなたはこのリポジトリを所有する組織に所属していません。",
    "UNAUTHORIZED::NO_PERMISSION": "あなたはこのリポジトリに対して十分な権限を持っていません。",
    "INVALID_ALIAS_NAME": "エイリアス名が不正です。",
    "UNABLE_TO_PARSE_REQUEST": "リクエストの解析に失敗しました。",
    "DUPLICATE": "既に同じエイリアスが存在します。",
}

ALIAS_ADDED_COMMENT = """
## :tada: あなたのエイリアスが追加されました！ :tada:

あなたのリクエストであるエイリアス **{alias_name}** が追加されました
<kbd>/kpm update</kbd> を実行してエイリアス定義ファイルをアップデートしてください。 
アップデート後、<kbd>/kpm install {alias_name}</kbd> コマンドでエイリアスを使用できるようになります。

"""
