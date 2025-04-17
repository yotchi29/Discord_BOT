import os
import re
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_PATH=f"{os.path.dirname(os.path.abspath(__file__))}/token.json"
CRED_PATH=f"{os.path.dirname(os.path.abspath(__file__))}/credentials.json"

# google API認証

# 認証とAPIクライアントの作成
def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            #offlineはリフレッシュトークン取得、consentは次回以降も取得可能にする
            creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# 動画URLから動画IDを抽出
def extract_video_id(video_url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, video_url)
    return match.group(1) if match else None

# プレイリストに動画を追加
def add_video_to_playlist(video_url):
    video_id = extract_video_id(video_url)
    youtube = get_authenticated_service()
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": "PLy1zTyKa-YM6sIw_wZ4aKyN4myTwglKnM", # 追加先のプレイリストID
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            }
        },
    )
    response = request.execute()


