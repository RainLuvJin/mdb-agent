def validate_result(result, schema):
    """
    检查 AI 返回的结果是否符合真实数据库 Schema。
    """

    # 1. 检查 table
    table_name = result.get("table")

    if table_name not in schema:
        raise ValueError(
            f"AI选择了不存在的表: {table_name}"
        )

    # 2. 获取 AI 返回的字段
    fields = result.get("fields", {})

    # 3. 获取这个表真实存在的字段
    valid_columns = {
        column["name"]: column
        for column in schema[table_name]
    }

    # 4. 检查 AI 有没有编造字段
    for field_name in fields:
        if field_name not in valid_columns:
            raise ValueError(
                f"AI返回了不存在的字段: "
                f"{table_name}.{field_name}"
            )

    # 5. 清理字段
    cleaned_fields = {}

    for field_name, value in fields.items():

        column = valid_columns[field_name]

        # 主键由数据库自动生成
        if column["primary_key"]:

            # 如果 AI 自己给了一个 id，直接拒绝
            if value is not None:
                raise ValueError(
                    f"不允许 AI 手动设置主键: "
                    f"{table_name}.{field_name}"
                )

            continue

        cleaned_fields[field_name] = value

    # 6. 返回通过验证后的结果
    return {
        "table": table_name,
        "reason": result.get("reason"),
        "fields": cleaned_fields
    }