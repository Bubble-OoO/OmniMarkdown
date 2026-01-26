import openai
import json


def load_client(config_path="config.json"):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        api_key = config.get("api_key")
        base_url = config.get("base_url")
        model_name = config.get("model_name")

        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        if not api_key:
            print("警告: 配置文件中未找到 api_key")

        return client, model_name

    except FileNotFoundError:
        print(f"错误: 配置文件 {config_path} 不存在")
        return None, None
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件格式错误 - {e}")
        return None, None
    except Exception as e:
        print(f"错误: 读取配置文件失败 - {e}")
        return None, None


class LLMConfig:
    def __init__(self, config_path="config.json"):
        self.client, self.model_name = load_client(config_path)
        if self.client is None:
            raise RuntimeError("LLM 客户端初始化失败")

    def chat(self, messages, **kwargs):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            timeout=100,
            **kwargs
        )
        return response.choices[0].message.content
