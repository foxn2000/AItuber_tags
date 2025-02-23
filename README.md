# AItuberのデータより、簡易的にタグを生成するAIシステム

## how to use

もとデータを"https://github.com/tegnike/aituber-list/tree/main/app/data/aitubers.json"より取得し、aitubers.jsonに保存する。
仮想環境に入り、必要なパッケージをインストールする。
```bash
python3 -m venv env
source venv/bin/activate
pip install -r requirements.txt
```
その後.env.exampleを.envにコピーし、適宜設定を行う。(youtube data api v3を使うため、以下の[ブログ](https://qiita.com/nbayashi/items/bde26cd04f08de21d552#準備)を参考にしてAPIキーを取得すること)

以下のコマンドを実行すると、タグを生成する。
```bash
python main.py
```