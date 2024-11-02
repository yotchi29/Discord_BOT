from pytubefix import YouTube

def get_youtube_url(link):
    yt = YouTube(link)

    streams = yt.streams
    audio = streams.filter(only_audio=True).order_by('abr').last()
    audio_url = audio.url

    return audio_url

#確認用
print(get_youtube_url("https://www.youtube.com/watch?v=5mNoe6THr0A&pp=ygUN44Op44Oe44O844K6cA%3D%3D"))