from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import os
load_dotenv()

client = genai.Client(
    http_options=types.HttpOptions(
        base_url=os.getenv("GOOGLE_API_BASE")
    ),
    api_key=os.getenv("GOOGLE_API_KEY")
)
print("client created")
# 1. 上传文件 (修正了之前的 file 参数名问题)
print("正在上传视频...")
myfile = client.files.upload(file="video/hot_video.mp4")
print(f"文件上传成功，初始状态: {myfile.state.name}")

# 2. 等待视频处理完成 (核心修复代码)
while myfile.state.name == "PROCESSING":
    print("视频正在后台处理中，请稍候...", end="\r")
    time.sleep(3)  # 每 3 秒检查一次
    # 必须通过 get 方法刷新文件对象的状态
    myfile = client.files.get(name=myfile.name)

if myfile.state.name == "FAILED":
    print("\n视频处理失败！")
    exit()

print(f"\n视频处理就绪 (状态: {myfile.state.name})，开始分析...")

# 3. 此时再发起分析请求
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[myfile, "请详细分析这个视频的内容"]
)

print("-" * 20)
print(response.text)
