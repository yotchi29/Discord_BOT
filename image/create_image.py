from openai import OpenAI
import config
import base64
import io

# OpenAIクライアントのインスタンス化
client = OpenAI(api_key=config.OPENAI_API_KEY)

def create_image(query):
    # 画像生成をリクエスト（dall-e-3は2026-03-04に廃止されたためgpt-image-1-miniを使用）
    response = client.images.generate(
        model="gpt-image-1-mini",
        prompt=query,
        quality="medium",  # low(最安)/medium/high。コストと画質のバランスでmedium
        size="1024x1024",
    )

    # gpt-image系はURLではなくbase64で画像データが返る
    image_data = io.BytesIO(base64.b64decode(response.data[0].b64_json))

    return image_data

