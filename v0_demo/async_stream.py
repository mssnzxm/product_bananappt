import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

async def main():
    # 使用 .aio 访问异步客户端
    client = genai.Client(
        http_options=types.HttpOptions(
            base_url=os.getenv("GOOGLE_API_BASE")
        ),
        api_key=os.getenv("GOOGLE_API_KEY")
    ).aio
    
    model_id = "gemini-3-flash-preview"
    
    # 异步迭代器
    async for chunk in await client.models.generate_content_stream(
        model=model_id,
        contents="写一个笑话，200字左右。"
    ):
        if chunk.text:
            print(chunk.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())