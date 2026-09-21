import os
import json

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
def analyze_document(markdown, schema):

    prompt = f"""
    你是一个数据库内容整理 Agent。

    用户上传了一篇 Markdown 文档。

    你的任务是：
    1. 判断这篇文档最适合存入哪个数据库表
    2. 根据数据库字段，将文档内容映射到对应字段
    3. 只能使用文档中能够明确得到的信息
    4. 如果某个字段没有可靠信息，返回 null
    5. 不要编造信息
    6. 返回严格 JSON，不要输出任何额外文字

    数据库 Schema：

    {json.dumps(schema, ensure_ascii=False, indent=2)}

    Markdown 文档：

    {markdown}

    请按照下面的 JSON 格式返回：

    {{
        "table": "表名",
        "reason": "为什么选择这个表",
        "fields": {{
            "字段名": "字段值"
        }}
    }}
    """
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)