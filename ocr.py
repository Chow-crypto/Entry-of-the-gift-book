import json,os
import requests
from dotenv import load_dotenv
load_dotenv()

import openai
# 使用环境变量配置密钥（不要硬编码）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# 默认模型（可按需更改）
DEFAULT_MODEL = "gpt-4o-mini"
def chat(prompt):
    resp = openai.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": prompt},
        ]
    )
    text = resp.choices[0].message.content.strip()
    return text

class OCRClient:
    def __init__(self, app_id: str, secret_code: str):
        self.app_id = app_id
        self.secret_code = secret_code

    def recognize(self, file_content: bytes, options: dict) -> str:
        # 构建请求参数
        params = {}
        for key, value in options.items():
            params[key] = str(value)

        # 设置请求头
        headers = {
            "x-ti-app-id": self.app_id,
            "x-ti-secret-code": self.secret_code,
            "x-ti-client-source": "sample-code-v1.0",
            # 方式一：读取本地文件
            "Content-Type": "application/octet-stream"
            # 方式二：使用URL方式
            # "Content-Type": "text/plain"
        }

        # 发送请求
        response = requests.post(
            f"https://api.textin.com/ai/service/v1/pdf_to_markdown",
            params=params,
            headers=headers,
            data=file_content
        )

        # 检查响应状态
        response.raise_for_status()
        return response.text

def OCR(img_file):
    # 创建客户端实例
    client = OCRClient("c5ebf6b186d78170160b75a702b6cdb6", "cc73863cb409822d2bc9c8e62a034db2")

    # 读取图片文件
    # 方式一：读取本地文件
    with open(img_file, "rb") as f:
        file_content = f.read()
    # 方式二：使用URL方式（需要将headers中的Content-Type改为'text/plain'）
    # file_content = "https://example.com/path/to/your.pdf"

    # 设置转换选项
    options = dict(
        crop_dewarp = 1, #切边矫正
        apply_document_tree=1,
        apply_merge=1,
        catalog_details=1,
        dpi=144,
        formula_level=1,
        get_excel=1,
        get_image="objects",
        markdown_details=1,
        page_count=1000,
        page_details=1,
        paratext_mode="annotation",
        parse_mode="vlm",
        table_flavor="html",
    )

    response = None
    try:
        response = client.recognize(file_content, options)
        
        # 保存完整的JSON响应到result.json文件
        with open("result.json", "w", encoding="utf-8") as f:
            f.write(response)
        
        # 解析JSON响应以提取markdown内容
        json_response = json.loads(response)
        if "result" in json_response and "markdown" in json_response["result"]:
            markdown_content = json_response["result"]["markdown"]
            with open("result.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
        
    except Exception as e:
        print(f"Error: {e}")
    return response



if __name__ == "__main__":
    OCR(img_file="example.png")