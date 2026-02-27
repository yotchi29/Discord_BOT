import discord
from discord.ext import commands, tasks
from pathlib import Path
import re, json, os

#独自.pyファイル
import config
from open_ai_api import get_response
from get_youtube_url import get_youtube_url
from create_voice import create_voice
from add_playlist import add_video_to_playlist
from create_image import create_image
import datetime
import random

#BOTトークン
TOKEN = config.BOT_TOKEN
YOUTUBE_PLAYLIST_URL = config.YOUTUBE_PLAYLIST_URL

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

# Discordのクライアントを設定
client = discord.Client(intents=intents)
  

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

    # 既に接続中の場合は切断してリセット
    if voice_client is not None and voice_client.is_connected():
        await voice_client.disconnect(force=True)
        voice_client = None

    # ユーザーのボイスチャンネルに接続
    voice_channel = ctx.author.voice.channel
    try:
        voice_client = await voice_channel.connect(reconnect=False)
    except discord.errors.ConnectionClosed as e:
        voice_client = None
        await ctx.send(f"ボイスチャンネルへの接続に失敗したのだ（コード: {e.code}）")
    except Exception as e:
        voice_client = None
        await ctx.send(f"ボイスチャンネルへの接続中にエラーが発生したのだ: {e}")

# 音声を停止し、ボイスチャンネルから切断するコマンド
@bot.command()
async def stop(ctx):
    global voice_client
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect(force=True)
        voice_client = None
        await ctx.send("ボイスチャンネルから切断したのだ")
    else:
        await ctx.send("ボイスチャンネルに接続していないのだ")

# ボットが強制切断された際にvoice_clientをリセット
@bot.event
async def on_voice_state_update(member, before, after):
    global voice_client
    if member == bot.user and before.channel is not None and after.channel is None:
        # ボット自身がボイスチャンネルから切断された
        if voice_client is not None:
            try:
                await voice_client.disconnect(force=True)
            except Exception:
                pass
            voice_client = None
            print("ボイスチャンネルから切断されたためvoice_clientをリセットしました")

@bot.command()
async def imggen(ctx, prompt):
    try:
        img_data=create_image(prompt)
        # Discordチャンネルに画像を送信
        #channel = client.get_channel(1362828942398193847)
        await ctx.send(file=discord.File(img_data, 'generated_image.jpg'))
        await ctx.send("画像の生成に成功したのだ")
    except: await ctx.send("画像の生成に失敗したのだ")

@tasks.loop(minutes=1)
async def daily_mention():
    now = datetime.datetime.now().strftime('%H:%M')
    if now == "12:00":
        # ボットが参加している全サーバーに対して実行
        for guild in bot.guilds:
            # 送信先チャンネルを選択（system_channel → 送信可能な最初のテキストチャンネル）
            channel = guild.system_channel or next(
                (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None
            )
            if not channel:
                print(f"{guild.name}: 送信可能なチャンネルが見つからなかったのだ")
                continue

            print(f"{guild.name} / #{channel.name}")

            # 既に指名したメンバーリスト読み込み（サーバーごとに管理）
            json_path = f"appointed_users_{guild.id}.json"
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        raw_users = json.load(f)
                        appointed_users = raw_users["members"]
                    print("appointed_users.json 読み込み成功")
                except Exception as e:
                    print("appointed_users.json の読み込みに失敗しました")
                    print(e)
                    appointed_users = []
            else:
                appointed_users = []
            print(f'既に指名されているメンバー：{appointed_users}')

            # チャンネルのメンバーリスト作成
            guild_members_list = [m for m in guild.members if not m.bot]
            guild_members = [m.global_name for m in guild_members_list]
            print(f'サーバーのメンバー：{guild_members}')

            # 抽選対象メンバーリスト作成
            lottery_list = list(set(guild_members) - set(appointed_users))
            # 全員呼ばれていたら初期化
            if not lottery_list:
                lottery_list = guild_members
                appointed_users = []
            print(f'指名抽選対象メンバー：{lottery_list}')

            # 指名メンバー抽出
            appoint_user = random.choice(lottery_list)
            print(f'指名メンバー：{appoint_user}')
            chosen = next((m for m in guild_members_list if m.global_name == appoint_user), None)
            if not chosen:
                continue
            await channel.send(f"{chosen.mention} さん、今日はあなたの日なのだ！🌟")
            daily_res = get_response("何か私に質問して。質問だけ返して。いつも同じ質問にならないように気を付けて")
            await channel.send(daily_res["text"])

            # 指名したメンバーを追加してリストを保存
            appointed_users.append(appoint_user)
            raw_appointed_users = {'members': appointed_users}
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(raw_appointed_users, f, ensure_ascii=False, indent=2)

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
async def play(ctx, url):
    global is_playing

    play_url=get_youtube_url(url)
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

@bot.command()
async def playlist(ctx, url):
    """URLをYouTubeプレイリストに追加する"""
    if not bool(url_pattern.match(url)):
        await ctx.send("有効なURLを指定してほしいのだ")
        return
    try:
        add_video_to_playlist(url)
        reply = "プレイリストに追加できたのだ！！"
        if YOUTUBE_PLAYLIST_URL:
            reply += f"\n以下で確認!\n{YOUTUBE_PLAYLIST_URL}"
        await ctx.send(reply)
    except:
        await ctx.send("技術的な問題が発生したのだ...")

@bot.event
async def on_message(message):
    # ボット自身のメッセージは無視
    if message.author.bot:
        await bot.process_commands(message)
        return

    # メンションされたら呼び出されたチャンネルに返信
    if bot.user in message.mentions:
        response = get_response(message.content)
        print(message)
        await message.channel.send(response["text"])

    # ボットが同サーバーでボイス接続中なら、どのチャンネルのメッセージでも読み上げ
    if (message.guild and voice_client is not None and voice_client.is_connected()
            and voice_client.guild == message.guild
            and message.author.voice
            and not bool(url_pattern.match(message.content))):
        create_voice(message.content)
        audio_source = discord.FFmpegPCMAudio(f"{Path(__file__).parent}/tmp_file/res_voice.wav")
        if not voice_client.is_playing():
            voice_client.play(audio_source, after=lambda e: print("再生終了:", e))

    # コマンド処理を明示的に呼び出す
    await bot.process_commands(message)


# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)