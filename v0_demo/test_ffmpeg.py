from moviepy import ColorClip
import os

def verify_with_absolute_path():
    # 获取当前脚本所在的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = "ffmpeg_test_confirm.mp4"
    output_path = os.path.join(current_dir, output_filename)
    
    print(f"当前脚本运行目录: {current_dir}")
    
    try:
        # 创建一个简单的绿色片段
        clip = ColorClip(size=(640, 480), color=(0, 255, 0), duration=1)
        
        print("开始写入视频...")
        # 显式指定写入路径
        clip.write_videofile(output_path, fps=24, codec="libx264", logger='bar')
        
        # 强制刷新文件系统缓存
        if os.path.exists(output_path):
            print("\n" + "Success".center(40, "="))
            print(f"文件已确认生成！")
            print(f"绝对路径: {output_path}")
            print(f"文件大小: {os.path.getsize(output_path)} bytes")
            print("=" * 40)
        else:
            print("\n" + "Error".center(40, "!"))
            print("程序运行结束但未检测到文件。")
            print("可能原因：MoviePy 2.2.1 的 temp 目录清理机制或权限限制。")
            
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    verify_with_absolute_path()