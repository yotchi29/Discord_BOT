
import discord
from discord.ext import commands
#import nest_asyncio

#独自.pyファイル
import config
from open_ai_api import get_response

#BOTトークン
TOKEN = config.BOT_TOKEN

#BOTに付与する権限類
intents = discord.Intents.default()
#intents.members = True # メンバー管理の権限
intents.message_content = True # メッセージの内容を取得する権限

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="!", # !でコマンドを実行
    case_insensitive=True, # コマンドの大文字小文字を区別しない ($hello も $Hello も同じ!)
    intents=intents # 権限を設定
)

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@bot.command()
async def ai(ctx, *arg):
  # メッセージ送信者がBotだった場合は無視する
    if ctx.author.bot:
        return

    if arg:
      # メッセージの返信
      response = get_response(arg)
      print(arg)
      await ctx.send(response)
    else:
      await ctx.send("コマンドに続けて質問したいことを教えてね！")

# Botの起動とDiscordサーバーへの接続
#nest_asyncio.apply()
bot.run(TOKEN)