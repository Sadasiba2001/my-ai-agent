from tools.python import run_python
from tools.filesystem import list_files, read_file, write_file


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_python": run_python,
}



def execute_tool(tool_name: str, arguments: dict) -> str:
    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool: {tool_name}"

    tool = TOOL_FUNCTIONS[tool_name]

    try:
        return tool(**arguments)
    except Exception as e:
        return f"Tool execution error: {e}"