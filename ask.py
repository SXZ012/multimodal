import os
import sys
import base64
import argparse
from openai import OpenAI

# ---------- 配置 ----------
api_key = os.getenv("API_KEY")
if not api_key:
    print("❌ 错误：请先设置环境变量 API_KEY，例如：export API_KEY='你的key'")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

# ---------- 工具函数 ----------
def encode_image(image_path):
    """将图片文件编码为 base64 字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ask_image(image_path, question=None):
    """对图片提问，若无问题则退化为详细描述"""
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在：{image_path}")
        sys.exit(1)

    print(f"🖼️  正在分析图片: {image_path}")
    base64_image = encode_image(image_path)

    # 根据是否提供问题，构造不同的提示词
    if question:
        prompt = question
        temperature = 0.3  # 提问时降低随机性，让回答更精准
        print(f"❓ 提问: {question}")
    else:
        prompt = "请详细描述这张图片的内容，包括物体、颜色、场景、可能的活动等。"
        temperature = 0.7

    try:
        response = client.chat.completions.create(
            model="glm-4v",
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
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=temperature,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        sys.exit(1)

# ---------- 主程序 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="对图片提问或描述图片，使用智谱 GLM-4V 多模态模型"
    )
    parser.add_argument("image", help="图片文件路径")
    parser.add_argument("--question", "-q", help="你想问图片的问题，例如'图里有几个人？'")
    args = parser.parse_args()

    answer = ask_image(args.image, args.question)
    print("\n📝 回答：")
    print(answer)