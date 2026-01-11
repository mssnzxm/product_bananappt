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

# 指定模型 ID
model_id = "gemini-3-flash-preview"

# 使用 generate_content_stream 进行流式调用
response_stream = client.models.generate_content_stream(
    model=model_id,
    contents="写一个笑话，200字左右。"
)

print("--- 开始接收流式响应 ---")
for chunk in response_stream:
    # chunk.text 包含了当前接收到的文本片段
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n--- 响应结束 ---")