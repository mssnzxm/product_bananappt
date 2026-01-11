import os
import re
import requests
from google import genai
from google.genai import types
from moviepy import VideoFileClip
from PIL import Image
import whisper
from dotenv import load_dotenv

# 加载环境变量（需提前在.env文件配置GEMINI_API_KEY）
load_dotenv()


# -------------------------- 1. 视频链接解析模块 --------------------------
class VideoLinkParser:
    """解析不同平台的视频链接，提取核心信息"""
    def __init__(self, link):
        self.link = link
        self.platform = self._detect_platform()
        self.video_id = None
        self.meta_data = {}

    def _detect_platform(self):
        """识别视频平台"""
        if "douyin" in self.link or "tiktok" in self.link:
            return "douyin"
        elif "kuaishou" in self.link:
            return "kuaishou"
        elif "youtube" in self.link:
            return "youtube"
        else:
            raise ValueError(f"暂不支持解析该平台链接: {self.link}")

    def parse(self):
        """解析链接，获取视频ID和元数据（示例以抖音为例）"""
        if self.platform == "douyin":
            # 抖音链接正则匹配（适配短链/长链）
            pattern = r"(?<=video/)\d+|(?<=\/)\d+(?=\?)"
            match = re.search(pattern, self.link)
            if match:
                self.video_id = match.group()
                # 模拟获取元数据（实际需调用平台API/爬虫，此处为示例）
                self.meta_data = {
                    "title": "爆款视频标题示例：XX技巧太实用了！",
                    "like_count": 125800,  # 点赞数
                    "comment_count": 8900,  # 评论数
                    "share_count": 56000,   # 分享数
                    "author": "有机系统",
                    "publish_time": "2026-01-05"
                }
            else:
                raise ValueError("抖音链接解析失败，请检查链接格式")
        return self

# -------------------------- 2. 视频内容提取模块 --------------------------
class VideoContentExtractor:
    """提取视频帧、音频转文字"""
    def __init__(self, video_path):
        self.video_path = video_path
        self.frames = []  # 存储关键帧
        self.audio_text = ""  # 音频转写文本

    def extract_key_frames(self, frame_count=5):
        """提取视频关键帧（均匀采样）"""
        clip = VideoFileClip(self.video_path)
        duration = clip.duration
        interval = duration / frame_count
        for i in range(frame_count):
            frame = clip.get_frame(i * interval)
            frame_path = f"frame_{i}.jpg"
            Image.fromarray(frame).save(frame_path)
            self.frames.append(frame_path)
        clip.close()
        return self

    def transcribe_audio(self):
        """音频转文字（使用whisper）"""
        model = whisper.load_model("small")  # 轻量级模型，可换small/large
        #result = model.transcribe(self.video_path, language="zh")
        result = model.transcribe(self.video_path,language="Chinese",fp16=False)
        self.audio_text = result["text"]
        return self

# -------------------------- 3. Gemini AI分析模块 --------------------------
class GeminiVideoAnalyzer:
    """调用Gemini分析爆款视频原因"""
    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        model: str = "gemini-2.5-pro"
        ):
        
        timeout_ms = int(60 * 1000)
        http_options = types.HttpOptions(
                base_url=api_base,
                timeout=timeout_ms
        ) if api_base else types.HttpOptions(timeout=timeout_ms)

        self.client = genai.Client(
                http_options=http_options,
                api_key=api_key
        )
        # 选择支持视频分析的最优模型：Gemini 2.5 Pro
        self.model = model

    def analyze(self, meta_data, frames, audio_text):
        """
        核心分析逻辑：
        - 传入元数据（爆款数据）+ 视频帧 + 音频文本
        - 提示词引导Gemini分析爆款原因
        """
        # 构造分析提示词
        prompt = f"""
        请你作为专业的短视频爆款分析师，分析以下视频成为爆款的核心原因：
        1. 视频基础信息：
           - 标题：{meta_data['title']}
           - 点赞数：{meta_data['like_count']}
           - 评论数：{meta_data['comment_count']}
           - 分享数：{meta_data['share_count']}
           - 发布者：{meta_data['author']}
        2. 视频音频内容：{audio_text}
        3. 分析要求：
           - 从内容价值、情感共鸣、传播性、受众匹配4个维度分析
           - 总结3个核心爆款原因，每个原因给出具体依据
           - 输出结构化结论，语言简洁易懂
        """

        # 构造输入内容（文本+图片帧）
        input_content = [prompt]
        # 添加视频帧（Gemini支持图片输入）
        for frame_path in frames:
            with open(frame_path, "rb") as f:
                # 读取图片数据并创建Blob对象
                image_data = f.read()
                blob = types.Blob(data=image_data, mime_type="image/jpeg")
                # 创建Part对象并添加到输入内容中
                image_part = types.Part(inline_data=blob)
                input_content.append(image_part)
        
        # 调用Gemini生成分析结果
        response = self.client.models.generate_content(
            model=self.model,
            contents=input_content
        )
        return response.text

# -------------------------- 4. 主流程整合 --------------------------
def analyze_hot_video(link, video_local_path):
    """
    主函数：输入爆款视频链接+本地视频路径，输出分析结果
    :param link: 视频链接
    :param video_local_path: 视频本地路径（需先下载视频）
    :return: 分析结论
    """
    try:
        # 步骤1：解析链接获取元数据
        parser = VideoLinkParser(link).parse()
        print("✅ 链接解析完成，视频元数据：", parser.meta_data)

        # 步骤2：提取视频内容（帧+音频文本）
        extractor = VideoContentExtractor(video_local_path)
        extractor.extract_key_frames(frame_count=5).transcribe_audio()
        print("✅ 视频内容提取完成，关键帧数量：", len(extractor.frames))
        print("✅ 音频转写完成，文本内容：", extractor.audio_text[:100] + "...")

        # 步骤3：AI分析爆款原因
        analyzer = GeminiVideoAnalyzer()
        analysis_result = analyzer.analyze(
            meta_data=parser.meta_data,
            frames=extractor.frames,
            audio_text=extractor.audio_text
        )

        # 清理临时帧文件
        for frame in extractor.frames:
            os.remove(frame)

        return analysis_result

    except Exception as e:
        return f"分析失败：{str(e)}"

# -------------------------- 测试运行 --------------------------
if __name__ == "__main__":
    # 替换为实际的爆款视频链接和本地路径
    HOT_VIDEO_LINK = "https://www.douyin.com/video/7570329176536845618"
    HOT_VIDEO_LOCAL_PATH = "video/hot_video.mp4"

    # 执行分析
    result = analyze_hot_video(HOT_VIDEO_LINK, HOT_VIDEO_LOCAL_PATH)
    print("\n===== 爆款视频分析结论 =====")
    print(result)