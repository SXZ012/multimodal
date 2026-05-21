import os
import base64
from openai import OpenAI

# 1. 读取环境变量中的 API Key
api_key = os.getenv("API_KEY")
if not api_key:
    print("❌ 错误：请先设置环境变量 API_KEY")
    exit(1)

# 2. 初始化客户端，base_url 指向智谱的兼容接口
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"  # 智谱的兼容地址
)

# 3. 把图片文件编码为 base64 字符串
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# 4. 核心函数：解读图片
def describe_image(image_path):
    print(f"🖼️  正在分析图片: {image_path}")
    
    # 获取图片的 base64 编码
    base64_image = encode_image(image_path)
    
    # 调用多模态模型，消息中直接包含图片
    response = client.chat.completions.create(
        model="glm-4v",  # GLM-4V 多模态模型
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请详细描述这张图片的内容，包括物体、颜色、场景、可能的活动等。"
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    # 提取返回的描述文字
    description = response.choices[0].message.content
    return description

# 5. 主程序：从命令行读取图片路径
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python describe.py <图片路径>")
        print("示例: python describe.py test.jpg")
        exit(1)
    
    image_path = sys.argv[1]
    result = describe_image(image_path)
    print("\n📝 AI的描述：")
    print(result)