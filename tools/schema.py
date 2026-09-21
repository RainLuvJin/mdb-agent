import sqlite3


def get_database_schema(db_path):
    conn = sqlite3.connect(db_path)

    schema = {}

    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    for (table_name,) in tables:
        columns = conn.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        schema[table_name] = []

        for column in columns:
            column_id, name, data_type, not_null, default_value, primary_key = column

            schema[table_name].append({
                "name": name,
                "type": data_type,
                "primary_key": bool(primary_key),
                "not_null": bool(not_null),
                "default": default_value
            })

    conn.close()

    return schema