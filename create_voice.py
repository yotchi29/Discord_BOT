import requests
from pathlib import Path

# ずんだもんの話者ID
speaker_id = 3

#入力：音声化したいメッセージ
def create_voice(text:str):
    # 音声合成用クエリを作成
    query_payload = {'text': text, 'speaker': speaker_id}
    query_res = requests.post("http://127.0.0.1:50021/audio_query", params=query_payload)
    query_res.raise_for_status()
    audio_query = query_res.json()

    # 音声合成を実行して音声データを生成
    synthesis_res = requests.post(
        "http://127.0.0.1:50021/synthesis", #ローカルでやるとき
        params={'speaker': speaker_id},
        json=audio_query
    )

    synthesis_res.raise_for_status()

    # 音声ファイルを保存して再生
    # __file__は実行ファイルの絶対パス
    with open(f"{Path(__file__).parent}/tmp_file/res_voice.wav", "wb") as f:
        f.write(synthesis_res.content)

    # 文字ファイルを保存(絶対パス)
    with open(f"{Path(__file__).parent}/tmp_file/res_text.txt", "w",encoding="utf-8") as f:
        f.write(text)

    print("音声・文字ファイルが生成されました！")
