from moviepy import ColorClip, VideoFileClip
import os

def check_moviepy_full_flow():
    filename = "final_test.mp4"
    
    try:
        # 1. 写入测试
        print("步骤 1: 正在创建并导出视频...")
        clip = ColorClip(size=(1280, 720), color=(50, 100, 255), duration=3)
        clip.write_videofile(filename, fps=30, codec="libx264", logger=None)
        
        # 2. 读取验证
        if os.path.exists(filename):
            print(f"步骤 2: 检测到文件 {filename}，正在尝试读取验证...")
            with VideoFileClip(filename) as video:
                print("-" * 30)
                print(f"验证成功！视频属性如下：")
                print(f" - 分辨率: {video.size}")
                print(f" - 时长: {video.duration} 秒")
                print(f" - 帧率: {video.fps} fps")
                print("-" * 30)
        
        print(f"\n验证完毕！文件保留在: {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"验证过程中出现异常: {e}")

if __name__ == "__main__":
    check_moviepy_full_flow()