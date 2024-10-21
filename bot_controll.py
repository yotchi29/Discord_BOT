import urllib.request
import imghdr
import PIL.Image
import discord
import re #正規表現のためのライブラリ
import nest_asyncio

##独自.pyファイル
import config
from open_ai_api import get_response

def tenpu_image_download(url, save_pass):
    #添付画像をダウンロード
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, save_pass)
    return

def download_image_class(message, save_pass):
  url = message.attachments[0].url
  tenpu_image_download(url, save_pass)
  # jpgに変換して上書き保存
  imagetype = imghdr.what(save_pass)

  if imagetype == "png":
    image_convert = PIL.Image.open(save_pass)
    image_convert = image_convert.convert("RGB")
    image_convert.save(save_pass)



save_pass = "/content/drive/MyDrive/tmp.jpg"

TOKEN = config.BOT_TOKEN

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
  # メッセージ送信者がBotだった場合は無視する
     if message.author.bot:
         return

    # 特定文字列から始まるものを検知
     if message.content:
      # if re.match("/ai.*", message.content) != None:
        response = get_response(message.content[4:])

        await message.channel.send(response)

nest_asyncio.apply()
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)