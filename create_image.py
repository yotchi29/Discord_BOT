from openai import OpenAI
import config
import requests
import io



# OpenAIクライアントのインスタンス化
client = OpenAI(api_key=config.OPENAI_API_KEY)

def create_image(query):
    # 画像生成をリクエスト
    response = client.images.generate(
    prompt=query,
    model="dall-e-3",
    n=1,  # 生成する画像の数
    size="1024x1024"  # 画像のサイズ
    )

    # 生成された画像のURLを取得
    image_url = response.data[0].url
    # 画像をリクエストして保存
    response = requests.get(image_url)
    image_data = io.BytesIO(response.content)

    return image_data

