from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(
    http_options=types.HttpOptions(
        base_url=os.getenv("GOOGLE_API_BASE")
    ),
    api_key=os.getenv("GOOGLE_API_KEY")
)


response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="AI时代一人公司可以开发哪些应用？",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)
        # 关闭思考模式:
        # thinking_config=types.ThinkingConfig(thinking_budget=0)
        # 开启动态思考:
        # thinking_config=types.ThinkingConfig(thinking_budget=-1)
    ),
)

print(response.text)