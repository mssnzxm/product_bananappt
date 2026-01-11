from google import genai
from google.genai import types

# 查看Part.from_bytes方法的详细信息
import inspect
if hasattr(types.Part, 'from_bytes'):
    print("Part.from_bytes方法的文档:", types.Part.from_bytes.__doc__)
    print("Part.from_bytes方法的签名:", inspect.signature(types.Part.from_bytes))

# 测试从文件创建Part对象
# 创建一个简单的测试图片文件
import PIL.Image
import io

# 创建一个100x100的红色图片
img = PIL.Image.new('RGB', (100, 100), color='red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()

# 尝试使用Part.from_bytes方法创建Part对象
print("\n尝试使用Part.from_bytes方法创建Part对象...")
try:
    image_part = types.Part.from_bytes(img_bytes, mime_type="image/jpeg")
    print("成功创建Part对象!")
    print("Part对象类型:", type(image_part))
    print("Part对象内容:", image_part)
except Exception as e:
    print(f"创建Part对象失败: {e}")

# 尝试直接使用Part构造函数创建Part对象
print("\n尝试直接使用Part构造函数创建Part对象...")
try:
    # 创建Blob对象
    blob = types.Blob(data=img_bytes, mime_type="image/jpeg")
    # 创建Part对象
    image_part = types.Part(inline_data=blob)
    print("成功创建Part对象!")
    print("Part对象类型:", type(image_part))
    print("Part对象内容:", image_part)
except Exception as e:
    print(f"创建Part对象失败: {e}")
