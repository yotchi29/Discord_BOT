
import discord
from discord.ext import commands, tasks
from pathlib import Path
import re

#独自.pyファイル
import config
from open_ai_api import get_response
from get_youtube_url import get_youtube_url
from create_voice import create_voice
from add_playlist import add_video_to_playlist
import datetime
import pytz
import random

#BOTトークン
TOKEN = config.BOT_TOKEN
GUILD_ID=config.GUILD_ID
CHANNEL_ID=config.DAILY_CHANNEL_ID



# グローバル変数としてvoice_clientを定義
voice_client = None

# URL検出用の正規表現パターン
url_pattern = re.compile(
    r'^(https?://(?:www\.)?[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)$'
)

#BOTに付与する権限類
intents = discord.Intents.default()
#intents.members = True # メンバー管理の権限
intents.message_content = True # メッセージの内容を取得する権限
intents.members = True  #メンバーを取得する権限

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
    daily_mention.start()


# メッセージ受信時に動作する処理
@bot.command(name="ai", description="AIずんだもんが応答します")
async def ai(ctx, *input_message):
  # メッセージ送信者がBotだった場合は無視する
    if ctx.author.bot:
        return

    if input_message:
        # メッセージの返信
        response = get_response(input_message)
        print(input_message)

        #話者がチャンネルにいて、voice_clientがチャンネルに接続されていることを確認
        if ctx.author.voice and voice_client is not None and voice_client.is_connected(): 
            # 音声ファイルのパスを指定
            create_voice(response["text"])
            audio_source = discord.FFmpegPCMAudio(f"{Path(__file__).parent}/tmp_file/res_voice.wav")
            if not voice_client.is_playing():
                voice_client.play(audio_source, after=lambda e: print("再生終了:", e))
        await ctx.send(response["text"])
   
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
    voice_client = await voice_channel.connect()# 音声データの取得と認識

# 音声を停止し、ボイスチャンネルから切断するコマンド
@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから切断したのだ")
    else:
        await ctx.send("ボイスチャンネルに接続していないのだ")

@tasks.loop(minutes=1)
async def daily_mention():
    now = datetime.datetime.now().strftime('%H:%M')
    if now == "12:00":
        guild = bot.get_guild(GUILD_ID)
        channel = bot.get_channel(CHANNEL_ID)
        print(guild)
        print(channel)

        if guild and channel:
            # bot 以外のメンバーを抽出
            members = [m for m in guild.members if not m.bot]
            if members:
                chosen = random.choice(members)
                await channel.send(f"{chosen.mention} さん、今日はあなたの日なのだ！🌟")
                daily_res=get_response("何か私に質問して。質問だけ返して。いつも同じ質問にならないように気を付けて")
                await channel.send(daily_res["text"])

#################################################################################
queue=[]
is_playing=False

def play_next(ctx, vc):
    global is_playing
    if queue:
        next_url = queue.pop(0)
        audio_source = discord.FFmpegPCMAudio(next_url)
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.25)
        vc.play(audio_source, after=lambda e: play_next(ctx, vc))
    else:
        is_playing = False

@bot.command()
async def play(ctx, play_url):
    global is_playing

    voice_client = ctx.voice_client
    if ctx.author.voice and voice_client and voice_client.is_connected():
        if not voice_client.is_playing() and not is_playing:
            is_playing = True
            audio_source = discord.FFmpegPCMAudio(play_url)
            audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.25)
            voice_client.play(audio_source,after=lambda e: play_next(ctx, voice_client))
        else:
            queue.append(play_url)
            await ctx.send(f"キューに追加したのだ")
#######################################################################################

@bot.event
async def on_message(message):
    if bot.user in message.mentions or any(role.id == 1309581086510153771 for role in message.role_mentions):
        # メッセージが送られてきたチャンネルに送る
        response = get_response(message.content)
        print(message)
        await message.channel.send(response["text"])
        
    #
    if message.channel.id == 1311371023245115442 and message.author.voice and voice_client is not None and voice_client.is_connected():
    #if message.channel.id == 818608655058337806 and message.author.voice and voice_client is not None and voice_client.is_connected(): 
        if not bool(url_pattern.match(message.content)):
            create_voice(message.content)
            audio_source = discord.FFmpegPCMAudio(f"{Path(__file__).parent}/tmp_file/res_voice.wav")
            voice_client.play(audio_source, after=lambda e: print("再生終了:", e))

    #if message.channel.id == 818608655058337806 and bool(url_pattern.match(message.content)):
    if message.channel.id == 1343922045355823155 and bool(url_pattern.match(message.content)):
            try:
                add_video_to_playlist(message.content)
                await message.channel.send("プレイリストに追加できたのだ！！\n以下で確認!\nhttps://www.youtube.com/playlist?list=PLy1zTyKa-YM6sIw_wZ4aKyN4myTwglKnM")
            except:
                await message.channel.send("技術的な問題が発生したのだ...")

    # コマンド処理を明示的に呼び出す
    await bot.process_commands(message)


# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)