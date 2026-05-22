import os
import sys
import base64
import json
import argparse
import time
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm

# ---------- 配置 ----------
api_key = os.getenv("API_KEY")
if not api_key:
    print("❌ 请先设置环境变量 API_KEY")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

# 支持的图片后缀
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_image(image_path, question=None):
    """分析单张图片，返回结果字典"""
    base64_image = encode_image(image_path)
    if question:
        prompt = question
        temperature = 0.3
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
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            temperature=temperature,
            max_tokens=1024
        )
        answer = response.choices[0].message.content
        return {
            "file": str(image_path),
            "question": question or "详细描述",
            "answer": answer,
            "status": "success"
        }
    except Exception as e:
        return {
            "file": str(image_path),
            "question": question or "详细描述",
            "answer": None,
            "status": "error",
            "error": str(e)
        }

def batch_analyze(folder, question=None, output="results.json", delay=0.5):
    """遍历文件夹，批量分析图片并保存JSON"""
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"❌ 文件夹不存在: {folder}")
        sys.exit(1)

    # 收集所有图片文件
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(folder_path.glob(f"*{ext}"))
        images.extend(folder_path.glob(f"*{ext.upper()}"))  # 处理大写后缀
    images = sorted(list(set(images)))  # 去重排序

    if not images:
        print(f"❌ 在 {folder} 中没有找到任何图片文件")
        sys.exit(1)

    print(f"📁 找到 {len(images)} 张图片，开始批量分析...\n")
    results = []
    for img_path in tqdm(images, desc="分析进度"):
        result = analyze_image(str(img_path), question)
        results.append(result)
        time.sleep(delay)  # 避免触发 API 频率限制

    # 写入 JSON
    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 统计
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n✅ 完成！成功 {success_count}/{len(images)} 张")
    print(f"📄 结果已保存至 {output}")

# ---------- 主程序 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量分析文件夹中的图片")
    parser.add_argument("folder", help="包含图片的文件夹路径")
    parser.add_argument("--question", "-q", help="对所有图片问同一个问题，不提供则默认详细描述")
    parser.add_argument("--output", "-o", default="results.json", help="结果输出文件，默认 results.json")
    parser.add_argument("--delay", "-d", type=float, default=0.5, help="每张图片处理后的等待时间（秒），默认0.5")
    args = parser.parse_args()

    batch_analyze(args.folder, args.question, args.output, args.delay)