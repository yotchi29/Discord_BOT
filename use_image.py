import urllib.request
import imghdr
import PIL.Image

def tenpu_image_download(url, save_pass):
    #添付画像をダウンロード
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, save_pass)
    return

def download_image(message, save_pass):
  url = message.attachments[0].url
  tenpu_image_download(url, save_pass)
  # jpgに変換して上書き保存
  imagetype = imghdr.what(save_pass)

  if imagetype == "png":
    image_convert = PIL.Image.open(save_pass)
    image_convert = image_convert.convert("RGB")
    image_convert.save(save_pass)

save_pass = "/content/drive/MyDrive/tmp.jpg"