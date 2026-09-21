import sqlite3


def generate_insert_sql(table_name, fields):
    """
    根据已经通过验证的字段，生成参数化 INSERT SQL。
    """

    if not fields:
        raise ValueError("没有可以插入的字段")

    columns = ", ".join(fields.keys())
    placeholders = ", ".join("?" for _ in fields)

    sql = f"""
INSERT INTO {table_name} ({columns})
VALUES ({placeholders});
""".strip()

    values = list(fields.values())

    return sql, values


def execute_insert(db_path, sql, values):
    """
    执行 INSERT SQL。
    """

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        cursor.execute(sql, values)

        conn.commit()

        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        
def find_duplicate(db_path, table_name, fields):
    """
    根据常见的唯一标识字段，检查数据库中是否已经存在相同记录。
    """

    # 不同表使用不同的主要识别字段
    identity_fields = {
        "projects": "title",
        "articles": "title",
        "perspective": "title",
        "experience": "name",
        "category": "name",
        "config": "key"
    }

    identity_field = identity_fields.get(table_name)

    # 当前表没有定义识别字段
    if not identity_field:
        return None

    # AI 没有返回这个字段
    if identity_field not in fields:
        return None

    identity_value = fields[identity_field]

    # 没有值，无法判断
    if identity_value is None:
        return None

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        sql = f"""
        SELECT *
        FROM {table_name}
        WHERE {identity_field} = ?
        LIMIT 1
        """

        cursor.execute(sql, (identity_value,))

        row = cursor.fetchone()

        return row

    finally:
        conn.close()