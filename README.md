# 多模态图片解读工具 CLI

一个命令行工具，调用智谱GLM-4V多模态大模型，只需传入图片路径，即可获得AI对图片的详细描述。

## 快速开始

### 1. 获取 API Key
去 [智谱AI开放平台](https://open.bigmodel.cn/) 注册并创建 API Key。

### 2. 安装依赖
`pip install openai`

### 3. 设置环境变量
`export API_KEY="你的key"`

### 4. 运行
`python describe.py test.jpg`

## 示例
`python describe.py my_photo.jpg`
> 🖼️ 正在分析图片: my_photo.jpg
>
> 📝 AI的描述：
> 这是一张户外风景照，画面中有蓝天、白云和一片金黄色的麦田，远处可见连绵的山脉...

## 后续计划
- [ ] 支持对图片提问（例如“图里有几个人？”）
- [ ] 支持批量处理文件夹
- [ ] 打包成可执行文件