from flask import Flask, render_template, request, jsonify
from flask import Flask, request, jsonify
from flask_cors import CORS  # 1. 导入
import os
# 导入你原有的工具类（确保路径正确）
from utils import load_client, read_file, prompt_manage

app = Flask(__name__)
CORS(app)

# --- 配置初始化 ---
FILE_PATH = "/user_files/notebook.md"
CLIENT_CONFIG = "/config/llm_config.json"
ANSWER_PROMPT = "/prompts/answer_prompt.txt"
EDIT_PROMPT = "/prompts/edit_markdown_prompt.txt"

# 全局初始化对象
prompts = prompt_manage.PromptManager(ANSWER_PROMPT, EDIT_PROMPT)
llm_model = load_client.LLMConfig(CLIENT_CONFIG)

def write_markdown(content):
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        
        print(f"收到请求: {user_input}")

        if not user_input:
            return jsonify({"error": "内容不能为空"}), 400

        md_content = read_file.read_markdown(FILE_PATH)
        
        if user_input.startswith('!') or user_input.startswith('！'):
            instruction = user_input[1:].strip()
            system_prompt = prompts.edit_system_prompt
            user_prompt = prompts.build_edit_prompt(md_content, instruction)
            
            new_content = llm_model.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            if write_markdown(new_content):
                return jsonify({"type": "edit", "result": "文档已更新保存", "content": new_content})
            else:
                return jsonify({"error": "文件写入失败"}), 500

        else:
            query = user_input[1:].strip() if (user_input.startswith('?') or user_input.startswith('？')) else user_input
            system_prompt = prompts.answer_system_prompt
            user_prompt = prompts.build_answer_prompt(md_content, query)
            
            answer = llm_model.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            return jsonify({"type": "query", "result": answer})

    except Exception as e:
        import traceback
        traceback.print_exc() 
        return jsonify({"error": f"后端逻辑崩溃: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)