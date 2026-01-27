# OmniMarkdown

## 一、 Environment Setup
(不需要算力，能安装Anaconda即可，如果希望能够长时间运行，请确保这台电脑(笔记本or台式机均可)长时间处于运行状态，网络稳定即可)

请确保你的服务器安装 Anaconda 或 Python 3.10+ 环境。

1. 创建虚拟环境
```
conda create -n omnimarkdown python=3.10
conda activate omnimarkdown
```

2. 安装必要依赖
```
pip install flask flask-cors openai cpolar
```

## 二、 系统配置

1. 配置 LLM API
(目前试过Qwen, Deepseek, Claude, Chatgpt和gemini，最后两个体验感最好，但其他的精准度也不错，就是会说些废话。)

修改 config/llm_config.json：
```
{
  "api_key": "your_api_key",
  "base_url": "https://api.openai.com/v1",
  "model": "your_selected_model"
}
```

## 三、 Quick Start
要实现远程访问，需要按顺序启动以下服务：

第一步：启动内网穿透
打开一个新的cmd窗口，启动 cpolar：
```
curl -L https://www.cpolar.com/static/downloads/install-release-cpolar.sh | sudo bash
cpolar http 5000
```

复制生成的 https://xxxx.r34.cpolar.top 公网地址。

第二步：配置前端 
```
打开 index.html。
修改 const API_BASE_URL 为你刚才复制的 cpolar https 地址。
```

第三步：启动服务
在项目根目录下运行：
```
cd omnimarkdown
python app.py
```
