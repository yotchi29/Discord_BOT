from pytubefix import YouTube

def get_youtube_url(link):
    yt = YouTube(link)

    streams = yt.streams
    audio = streams.filter(only_audio=True).order_by('abr').last()
    audio_url = audio.url

    return audio_url