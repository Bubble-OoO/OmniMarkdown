'''
读取用户 Markdown 文件内容
'''
def read_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return None, f"读取文件失败: {e}"
    return content, None


'''
读取txt文档
'''
def read_txt(file_path):
    """读取整个txt文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
    except Exception as e:
        print(f"读取文件时出错: {e}")