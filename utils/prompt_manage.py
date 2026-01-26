from utils import read_file

class PromptManager:
    """Prompt 管理器"""
    
    def __init__(self, answer_prompt_path: str, edit_prompt_path: str):
        self.answer_system_prompt = read_file.read_txt(answer_prompt_path)
        self.edit_system_prompt = read_file.read_txt(edit_prompt_path)
    
    def build_answer_prompt(self, md_content: str, user_query: str) -> str:
        """构建查询问答的 prompt"""
        return f"""
            以下是 Markdown 文档内容：
            ---
            {md_content}
            ---
            用户问题：{user_query}

            请结合上方文档内容给出准确回答。
            """
    
    def build_edit_prompt(self, md_content: str, user_instruction: str) -> str:
        """构建编辑文档的 prompt"""
        return f"""
            当前 Markdown 文档内容：
            ---
            {md_content}
            ---
            用户编辑指令：{user_instruction}
            请分析用户意图（增加/删除/修改），并据此更新文档内容，返回完整的更新后的 Markdown 文本。
            """
