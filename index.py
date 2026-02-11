from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field
import json
import psycopg

mcp = FastMCP(
  name = "数据库查询助手",
  instructions="""
    这个服务提供了一系列（目前只有一个）各种数据库的查询工具，可以通过传递一个合法（或不合法）的查询语句来进行查询。
  """,
)

@mcp.tool
def getFile(
    db_host: Annotated[str, "数据库服务器的IP地址，通常是是IP地址的形式。"], 
    db_port: Annotated[str, "数据库服务器的端口，可能单独提供，也可能和地址以冒号相连接。"], 
    db_user: Annotated[str, "数据库用户名，通常是纯英文和数字组成，极少包含特殊字符。"], 
    db_password: Annotated[str,  """
      数据库密码，长度通常在8位以上，并且通常包含符号。
      如果密码后面会跟随标点符号则有可能是密码的一部分，比如对话为密码是password01!，那么结尾的叹号也是密码的一部分而不表达语气。
    """], 
    db_name: Annotated[str, "数据库实例名称，通常表现为有逻辑的英文单词或拼音缩写。"], 
    sql_query: Annotated[str, "用户提供的SQL查询语句。"], 
) -> str:
    try:
        with psycopg.connect(
            host=db_host, port=db_port, user=db_user, password=db_password, dbname=db_name
        ) as connection:
            with connection.transaction(): # 开启只读事务
                connection.set_read_only(True)
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    
                    column_names = [desc[0] for desc in cursor.description] # 获取列名
                    rows = cursor.fetchall() # 获取查询结果
                    
                    # 将结果转换为字典列表（包含列名）
                    result_list = []
                    for row in rows:
                        row_dict = dict(zip(column_names, row))
                        result_list.append(row_dict)
                    
                    # 转换为 JSON 字符串
                    json_string = json.dumps(result_list, ensure_ascii=False, indent=2, default=str)
        return json_string

    except psycopg.Error as e:
        raise ToolError(f"数据库错误: {e}")
    except Exception as e:
        raise ToolError(f"发生错误: {e}")

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
