import os
import sqlite3
from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv()

db_path = os.getenv("DATABASE_PATH")
conn = sqlite3.connect(db_path)

# ① 接收 markdown 文件
def read_markdown(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileExistsError
    if path.suffix.lower() != ".md":
        raise ValueError("请上传 Markdown 文件（.md）")

    return path.read_text(encoding="utf-8")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python agent.py <markdown文件>")
        sys.exit(1)

    file_path = sys.argv[1]
    markdown = read_markdown(file_path)

    print("========== Markdown ==========")
    print(markdown)
    print("==============================")
#         ↓
# ② 读取 SQLite Schema
from tools.schema import get_database_schema
schema = get_database_schema(db_path)
#         ↓
# ③ 调 DeepSeek 返回 JSON
from tools.llm import analyze_document
import json
result = analyze_document(markdown, schema)
#         ↓
# ④ 打印字段映射
print("\n========== AI Result ==========")
print(json.dumps(result, ensure_ascii=False, indent=2))
#         ↓
# ⑤ 验证
from tools.validator import validate_result
validated_result = validate_result(result, schema)

print("\n========== Validated Result ==========")
print(json.dumps(validated_result, ensure_ascii=False, indent=2))
#         ↓
# ⑥ 生成 SQL
from tools.database import generate_insert_sql, execute_insert, find_duplicate
sql, values = generate_insert_sql(
    validated_result["table"],
    validated_result["fields"]
)

print("\n========== SQL Preview ==========")
print(sql)

print("\n========== Values ==========")
print(values)
#         ↓
# ⑦ 暂时不要执行

# ⑧ 用户确认
duplicate = find_duplicate(
    db_path,
    validated_result["table"],
    validated_result["fields"]
)

if duplicate:
    print("\n⚠️ 发现可能的重复记录！")
    print("数据库中已经存在相同的记录：")
    print(duplicate)

    confirm = input(
        "\n仍然要插入吗？(y/n): "
    ).strip().lower()

else:
    confirm = input(
        "\n是否写入数据库？(y/n): "
    ).strip().lower()


if confirm == "y":
    new_id = execute_insert(
        db_path,
        sql,
        values
    )

    print(f"\n✅ 写入成功！新记录 ID: {new_id}")

else:
    print("\n❌ 已取消写入。")
#         ↓
# ⑨ SQLite INSERT