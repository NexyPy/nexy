
## 2 つのルーター、1 つのフレームワーク

Nexy は **2 つのルーティング戦略**を提供しています。プロジェクトに合ったものを選択してください。

### Routes ルーター (ファイルベースのルーティング)

ルートはファイル ツリーによって定義されます。`src/routes/` 内のすべての `.nexy`、`.mdx`、または `.py` ファイルは自動的に HTTP ルートになります。

```text
src/routes/
├── index.nexy          →  /
├── about.nexy          →  /about
├── blog/
│   ├── index.nexy      →  /blog
│   └── [slug].nexy     →  /blog/{slug}
└── api/
    └── users.py        →  /api/users (GET, POST, etc.)
```**最適な用途**: シンプルなサイト、ドキュメント、MVP、API のみのプロジェクト、構成よりも規則を好むチーム。

詳細: [File-Based Routing →](/docs/fbrouters)

### モジュラールーター (デコレータベース)

ルートは Python デコレーターによって定義されます。NestJS パターンに従って、コードを **コントローラー**、**プロバイダー**、**モジュール**に編成します。

```python
from nexy.decorators import Controller

"@Controller("/users")
class UsersController:
    def __init__(self, service: UserService):
        self.service = service

    def GET(self):
        return self.service.find_all()
```**最適な用途**: 大規模なアプリケーション、ドメイン駆動設計、依存関係の挿入と厳密なコード編成の恩恵を受けるプロジェクト。

詳細: [Modular Router →](/docs/modular/overview)

> サイドバーの上部にある **ルーター セレクター** を使用して、各ルーターのドキュメント ビューを切り替えます。
