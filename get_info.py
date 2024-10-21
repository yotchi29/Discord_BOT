##################いったん凍結#########################
# from googleapiclient.discovery import build
# import config

# # youtubeのAPI設定
# YOUTUBE_API_KEY = config.YOU
# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_VERSION = 'v3'

# youtube = build(
#     YOUTUBE_API_SERVICE_NAME,
#     YOUTUBE_API_VERSION,
#     developerKey=YOUTUBE_API_KEY
# )

# #動画の情報をとってくる
# def get_video_info(keyword):
#     # search settings
#     youtube_query = youtube.search().list(
#         part='id,snippet',
#         q=keyword,
#         type='video',
#         maxResults=1,
#         order='relevance',
#     )

#     # execute()で検索を実行
#     youtube_response = youtube_query.execute()

#     # 検索結果を取得し、リターンする
#     return youtube_response.get('items', [])


