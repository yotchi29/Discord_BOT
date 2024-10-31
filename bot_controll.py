
import discord
from discord.ext import commands
from pathlib import Path

#独自.pyファイル
import config
from open_ai_api import get_response

#BOTトークン
TOKEN = config.BOT_TOKEN

# グローバル変数としてvoice_clientを定義
voice_client = None

#BOTに付与する権限類
intents = discord.Intents.default()
#intents.members = True # メンバー管理の権限
intents.message_content = True # メッセージの内容を取得する権限

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="!", # !でコマンドを実行
    case_insensitive=True, # コマンドの大文字小文字を区別しない
    intents=intents # 権限を設定
)

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print("ログインしました")

# メッセージ受信時に動作する処理
@bot.command()
async def ai(ctx, *input_message):
  # メッセージ送信者がBotだった場合は無視する
    if ctx.author.bot:
        return

    if input_message:
        # メッセージの返信
        response = get_response(input_message)
        print(input_message)
        await ctx.send(response["text"])
        
        #話者がチャンネルにいて、voice_clientがチャンネルに接続されていることを確認
        if ctx.author.voice and voice_client is not None and voice_client.is_connected(): 
            # 音声ファイルのパスを指定
            audio_source = discord.FFmpegPCMAudio(f"{Path(__file__).parent}/tmp_file/res_voice.wav")
            if not voice_client.is_playing():
                voice_client.play(audio_source, after=lambda e: print("再生終了:", e))
   
    else:
      await ctx.send("コマンドに続けて質問したいことを教えてね！")

# ボイスチャンネルに参加し、音声ファイルを再生するコマンド
@bot.command()
async def join(ctx):
    global voice_client #global変数のvoice_clientを指定、そうしないとaiコマンドで呼び出せない

    # ボイスチャンネルにユーザーがいるか確認
    if ctx.author.voice is None:
        await ctx.send("ボイスチャンネルに参加してください。")
        return

    # ユーザーのボイスチャンネルに接続
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    # if ctx.author.voice is None:
    #     # 音声ファイルのパスを指定
    #     audio_source = discord.FFmpegPCMAudio(f"{Path(__file__).parent}/tmp_file/res_voice.wav")
    #     if not voice_client.is_playing():
    #         voice_client.play(audio_source, after=lambda e: print("再生終了:", e))

# 音声を停止し、ボイスチャンネルから切断するコマンド
@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから切断しました。")
    else:
        await ctx.send("ボイスチャンネルに接続していません。")

# Botの起動とDiscordサーバーへの接続
#nest_asyncio.apply()
bot.run(TOKEN)