import json
import os

from googleapiclient.discovery import build
import google.generativeai as genai

from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

genai.configure(
    api_key = os.environ.get("GEMINI_API_KEY"),
)

def gemini_inference(user_inputs, system_prompt, main_model="gemini-2.0-flash-lite-preview-02-05"):
    if isinstance(user_inputs, str):
        try:
            gemini_model = genai.GenerativeModel(
                model_name=main_model,
                system_instruction=system_prompt,
            )
            gemini_chat = gemini_model.start_chat(history=[])
            response = gemini_chat.send_message(user_inputs)
            return response.text
        except Exception as e:
            # エラーが出た場合は空文字列を返す
            print(f"Geminiエラー: {e}")  # ログを残したい場合はprintやloggingなどを使う
            return ""
    else:
        return ""

SYSTEM_PROMPT = """
あなたは「AItuberの配信タイトル・概要欄」を“複数”読み取り、チャンネル単位で該当するタグを付与する専門のAIエージェントです。ユーザーは同じチャンネル内の複数の配信情報（タイトルと概要欄のセット）をまとめて提示します。あなたはそれら全体を通じて判断し、そのチャンネルに付与すべきタグを一度だけ出力してください。以下のルールを厳守し、問い合せが来た際には適切にタグを抽出・回答してください。
---
## 役割と目的

- **役割**: あなたは複数の配信タイトルと概要欄を総合して、そのチャンネルがどのような特徴を持つAITuberチャンネルであるかをタグで表します。  
- **目的**: チャンネル全体がどのようなコンテンツを配信しているのかを、定義されたタグを使って簡潔に表すことを目指します。
---
## タグの定義とチャンネル単位での抽出基準

以下のタグの定義はいずれも「チャンネルに該当するか」を判断するものです。  
複数の配信タイトル・概要欄に対して、一つでも該当する要素があれば、そのタグをチャンネルの特徴として付与します。

1. **コメント応答**  
   - チャットやコメントへの応答を行っている配信が1つでもある場合。  
   - 例: 「視聴者のコメントに答えるよ」「質問受付」などが複数配信のいずれかに含まれている。

2. **解説**  
   - 何かのテーマを解説・講座形式で配信している回が1つでもある場合。  
   - 例: 「〇〇の解説」「詳しく説明」など。

3. **海外**  
   - 日本語以外の言語で配信している回が1つでもある場合、または海外在住/海外出身を公言している回がある場合。  
   - 例: 「English Only Stream」「海外から配信」など。

4. **歌唱あり**  
   - 歌やカラオケ配信を行っている回が1つでもある場合。  
   - 例: 「歌枠」「歌配信」「歌ってみた」など。

5. **複数キャラ**  
   - 同チャンネル内で2体以上のAITuberやAIキャラクターが登場する回が1つでもある場合。  
   - 例: 「コラボ配信（AIキャラ同士）」「二人のAIが登場」など。

6. **ゲーム実況**  
   - ゲームをプレイしながらの実況配信を行っている回が1つでもある場合。  
   - 例: 「ゲーム配信」「○○を実況プレイ」など。

7. **一部AITuber**  
   - 普段は人間やVtuberとして配信しており、一部の回のみAITuberとして活動しているという趣旨の回が1つでも確認できる場合。  
   - 例: 「今日だけAIキャラ」「この回だけAITuberで配信」など。

8. **AIパートナー**  
   - 配信のメインは人間で、AITuberがアシスタント的にサブで登場している配信回が1つでもある場合。  
   - 例: 「人間メイン＋AIのサポート配信」「AIが人間を手伝う形で登場」など。
---
## 回答フォーマット

1. 全部の配信情報（タイトル・概要欄）を総合した上で、チャンネルとして該当するタグを **すべて半角カンマ区切り** で出力してください。  
2. 該当するタグが一つもない場合は、**「該当なし」** と出力してください。  
3. タグは上記で定義されたもののみに限定し、それ以外は追加しないでください。  
---
### 入力例
（同じチャンネルの複数の配信情報をまとめて提示したケース）

- 配信1: 「視聴者の質問に答えつつ、英語勉強配信」  
- 概要欄: 「コメント大歓迎。海外リスナーさんともコミュニケーションしたいです！」  

- 配信2: 「【ゲーム実況】RPGをクリア目指すよ」  
- 概要欄: 「初見プレイです！」  

- 配信3: 「歌ってみたを初公開！」  
- 概要欄: 「カラオケでAIボーカルに挑戦します！」  

### 出力例
`コメント応答, ゲーム実況, 歌唱あり`
---
上記例では「視聴者の質問に答える」→コメント応答  
「海外リスナーとコミュニケーション」→海外  
「RPG実況」→ゲーム実況  
「歌ってみた」→歌唱あり  
という要素がそれぞれ異なる回に含まれているため、チャンネル全体としてそれらが該当します。
---
以上のルールに基づき、ユーザーから提示される**同一チャンネルの複数配信のタイトルと概要欄**をすべて確認し、合致するタグのみを選び出し、**一度だけ**半角カンマ区切りで出力してください。該当する要素がない場合は「該当なし」と返答してください。
"""

def get_archived_streams(api_key, channel_id, max_results=20):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # まずは検索で動画IDだけ取得する
    search_request = youtube.search().list(
        part='id',
        channelId=channel_id,
        eventType='completed',
        type='video',
        order='date',
        maxResults=max_results
    )
    search_response = search_request.execute()
    
    # 動画IDをリスト化
    video_ids = [
        item['id']['videoId']
        for item in search_response.get('items', [])
        if item.get('id', {}).get('videoId')
    ]
    
    if not video_ids:
        return ""
    
    # videos.list でタイトルと概要欄を取得
    videos_request = youtube.videos().list(
        part='snippet',
        id=','.join(video_ids)
    )
    videos_response = videos_request.execute()
    
    results = []
    for item in videos_response.get('items', []):
        snippet = item.get('snippet', {})
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        results.append((title, description))
    
    # 結果を一つの文字列にまとめる
    result_str = ""
    for title, description in results:
        result_str += f"タイトル:{title}\n"
        result_str += f"概要欄:{description}\n"
        result_str += "-----------\n"
    
    return result_str

def main():
    API_KEY = os.environ.get("GOOGLE_PROJECT_API_KEY")
    
    # 1. data.json があるならそちらを、なければ aitubers.json を読み込む
    if os.path.exists("data.json"):
        print("data.json が見つかりました。続きから処理を再開します。")
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("data.json が存在しません。aitubers.json から読み込みます。")
        with open("aitubers.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    
    aitubers = data.get("aitubers", [])
    
    # 2. 各 AItuber のタグを更新
    for idx, aituber in enumerate(aitubers):
        channel_id = aituber.get("youtubeChannelID")
        
        # すでにタグが設定されている場合はスキップする（必要に応じて削除してください）
        if "tags" in aituber and aituber["tags"]:
            print(f"チャンネルID {channel_id} はすでにタグが設定されています。スキップします。")
            continue
        
        print(f"[{idx+1}/{len(aitubers)}] {channel_id} の配信情報を取得します...")
        archived_streams = get_archived_streams(API_KEY, channel_id, max_results=20)
        
        if not archived_streams:
            print(f"チャンネルID {channel_id} は動画が見つかりません。タグを空にします。")
            aituber["tags"] = []
        else:
            # Gemini API へ投げてタグ候補を取得
            results = gemini_inference(archived_streams, SYSTEM_PROMPT)
            print(f"推定タグ出力: {results}")
            
            # 実際に付与するタグを絞り込み
            tags = []
            if "コメント応答" in results: tags.append("コメント応答")
            if "解説" in results: tags.append("解説")
            if "海外" in results: tags.append("海外")
            if "複数キャラ" in results: tags.append("複数キャラ")
            if "歌唱あり" in results: tags.append("歌唱あり")
            if "ゲーム実況" in results: tags.append("ゲーム実況")
            if "一部AITuber" in results: tags.append("一部AITuber")
            if "AIパートナー" in results: tags.append("AIパートナー")
            
            if len(tags) == 0:
                # 「該当なし」が出力される可能性があれば、ここでチェック
                # ChatGPTが "該当なし" と出力したケースも想定して、空にしておく
                aituber["tags"] = []
            else:
                aituber["tags"] = tags
        
        # 3. ここでループ1回ごとに data.json に書き込み（上書き）する
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"チャンネルID {channel_id} のタグを data.json に保存しました。")
        print("-------------------------------------------------------------")
    
    print("すべてのタグ更新処理が完了しました。")

if __name__ == "__main__":
    main()
