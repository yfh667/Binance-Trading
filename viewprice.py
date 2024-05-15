import sqlite3

def get_price_history_by_token_id(db_name, token_id):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 准备 SQL 查询语句
    query = "SELECT price, timestamp FROM price_history WHERE token_id = ? ORDER BY timestamp"
    
    # 执行查询
    cursor.execute(query, (token_id,))
    
    # 获取所有查询结果
    results = cursor.fetchall()
    
    # 关闭数据库连接
    conn.close()
    
    # 返回结果
    return results
# Example to print the schema
def print_table_schema(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tokens);")
    print(cursor.fetchall())
    cursor.execute("PRAGMA table_info(price_history);")
    print(cursor.fetchall())
    conn.close()

# 使用函数获取 token ID 为 1 的历史价格
history = get_price_history_by_token_id('test.db', 1)
# 打印历史价格数据
print("Historical Prices for Token ID 1:")
for price, timestamp in history:
    print(f"Price: {price}, Timestamp: {timestamp}")
