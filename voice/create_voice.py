from pathlib import Path
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile, UserDict
from voicevox_core import UserDictWord

# 0.vvmに含まれるキャラクター（ノーマルスタイル）の話者ID
CHARACTERS = {
    "ずんだもん": 3,
    "四国めたん": 2,
    "春日部つむぎ": 8,
    "雨晴はう": 10,
}

# 現在読み上げに使用する話者ID（デフォルトはずんだもん）
speaker_id = CHARACTERS["ずんだもん"]

_ASSETS_DIR = Path(__file__).parent / "voicevox_core_assets"

# 初回import時にのみロードし、以降はプロセス内で使い回す
_onnxruntime = Onnxruntime.load_once(
    filename=str(_ASSETS_DIR / "onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3")
)
_open_jtalk = OpenJtalk(str(_ASSETS_DIR / "dict/open_jtalk_dic_utf_8-1.11"))
_synthesizer = Synthesizer(_onnxruntime, _open_jtalk)
with VoiceModelFile.open(str(_ASSETS_DIR / "models/vvms/0.vvm")) as _model:
    _synthesizer.load_voice_model(_model)

# ユーザー辞書（読み上げ用語の追加登録）。Bot全体で共通の1つを使い回す
_USER_DICT_PATH = Path(__file__).parent / "user_dictionary.json"
_user_dict = UserDict()
if _USER_DICT_PATH.exists():
    _user_dict.load(str(_USER_DICT_PATH))
_open_jtalk.use_user_dict(_user_dict)

#辞書に単語を追加（アクセント型は平板固定）
def add_dictionary_word(word: str, reading: str):
    _user_dict.add_word(UserDictWord(surface=word, pronunciation=reading, accent_type=0, word_type="PROPER_NOUN"))
    _user_dict.save(str(_USER_DICT_PATH))
    _open_jtalk.use_user_dict(_user_dict)  # 変更を反映するには再適用が必要

#辞書から単語を削除。存在しなければFalseを返す
def remove_dictionary_word(word: str) -> bool:
    matched_uuid = next((uuid for uuid, w in _user_dict.to_dict().items() if w.surface == word), None)
    if matched_uuid is None:
        return False
    _user_dict.remove_word(matched_uuid)
    _user_dict.save(str(_USER_DICT_PATH))
    _open_jtalk.use_user_dict(_user_dict)
    return True

#登録済み単語一覧を{単語: 読み}の形で取得
def list_dictionary_words() -> dict:
    return {w.surface: w.pronunciation for w in _user_dict.to_dict().values()}

#現在のキャラクターを変更
def set_character(name: str):
    global speaker_id
    speaker_id = CHARACTERS[name]

#現在のキャラクター名を取得
def get_character() -> str:
    return next(name for name, sid in CHARACTERS.items() if sid == speaker_id)

#入力：音声化したいメッセージ
def create_voice(text:str):
    # 音声合成用クエリを作成して音声データを生成
    audio_query = _synthesizer.create_audio_query(text, speaker_id)
    wav_data = _synthesizer.synthesis(audio_query, speaker_id)

    # 音声ファイルを保存して再生（tmp_fileはプロジェクトルート直下）
    tmp_dir = Path(__file__).parent.parent / "tmp_file"
    with open(tmp_dir / "res_voice.wav", "wb") as f:
        f.write(wav_data)

    # 文字ファイルを保存
    with open(tmp_dir / "res_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("音声・文字ファイルが生成されました！")
